import re

from contextlib import contextmanager

from django.db import DatabaseError
from django.db.models import Count, Q
from rest_framework.exceptions import PermissionDenied, ValidationError
from service_objects import fields as f

from biosql.models import Taxon
from submission.models import (
    Package,
    PackageSequencingData,
    SampleAlias,
    Sample,
    SequencingData,
)
from . import Service


class MatchingService(Service):
    """Submission data package matching service."""

    SAMPLE_PREFIX_DELIMITER = "_"

    package = f.ModelField(Package, required=True)
    """Package in a DRAFT|REJECTED state."""

    BIOSAMPLE_ORIGIN_PATTERN = re.compile(r"^SAM(N|EA)\d+$", re.IGNORECASE)
    SRS_ORIGIN_PATTERN = re.compile(r"^[ES]RS\d+$", re.IGNORECASE)
    LIBRARY_NAME_PATTERN = re.compile(r"^[SED]RR\d+$", re.IGNORECASE)

    @contextmanager
    def lock_package(self):
        """Lock package from changes, and change it's state after process finished."""
        package: Package = self.cleaned_data["package"]

        try:
            # acquire explicit lock on the package,
            # don't wait for existing lock to release
            # don't replace cleaned_data[package] to have original object updated
            self.cleaned_data["_package_locked"] = (
                Package.objects.editable()
                .select_for_update(nowait=True)
                .get(pk=package.pk)
            )
        except DatabaseError as exc:  # package is already locked
            raise PermissionDenied("Package is already being processed") from exc

        package.refresh_from_db()

        yield

        # finally, mark package as matched and save
        package.matching_state = package.MatchingState.MATCHED
        package.save()

    def process(self):
        """
        Perform package data matching.

        Sample aliases (and then mic/pds tests) being matched to samples:
        - by fastq file prefix.
            Prefix is optional for an alias, but required to be unique within package,
                so every alias has only one unique prefix or doesn't have any.
            There could be multiple fastqs by one prefix, and we need to make sure
                that every fastq with same prefix either linked to same sample,
                or not linked to any sample.
            At matching stage, we propagate this one sample to all fastqs in the group.
            And if there is no sample in whole group, we create one from the alias.

        - by alias name.
            - among NCBI/SRA submitted aliases, in alias name
            - among all FASTQ's in library_name
            - among user aliases, submitted earlier and approved, also in alias name
        """
        with self.lock_package():
            self.perform_match()

    def reset_match_state(self, package: Package):
        """Reset all data, that was generated during previous match."""
        if package.matching_state == package.MatchingState.NEVER_MATCHED:
            return

        package.sample_aliases.update(
            verdicts=[],
            match_source=None,
            sample=None,
        )
        package.mic_tests.update(sample=None)
        package.pds_tests.update(sample=None)

        package.assoc_sequencing_datas.update(verdicts=[])
        package.samples.all().delete()

    def perform_match(self):
        """Perform matching procedure."""
        package: Package = self.cleaned_data["package"]

        # check, if there's any data at all
        fastqs_cnt = package.sequencing_datas.count()
        aliases_cnt = package.sample_aliases.count()
        if not fastqs_cnt and not aliases_cnt:
            raise ValidationError("Package has no data")

        # remove previous run results
        self.reset_match_state(package)

        # Step 0: match aliases by name with specific pattern
        alias: SampleAlias
        for alias in package.sample_aliases.all():
            self.match_alias_by_pattern(alias)

        # Step 1: try to match all aliases by their name
        alias: SampleAlias
        for alias in package.sample_aliases.filter(match_source__isnull=True):
            self.match_alias_by_name(alias)

        # Step 2: for those, who hasn't matched and have fastq prefix,
        # try to match by prefix
        unmatched_with_prefix = package.sample_aliases.filter(
            fastq_prefix__isnull=False,
            match_source__isnull=True,
        )
        alias: SampleAlias
        for alias in unmatched_with_prefix:
            self.match_alias_by_prefix_or_sample_id(alias)

        # Step 2a: for those who have not yet matched
        # use the sample id as fastq prefix

        unmatched_no_prefix = package.sample_aliases.filter(
            fastq_prefix__isnull=True,
            match_source__isnull=True,
        )

        alias: SampleAlias
        for alias in unmatched_no_prefix:
            self.match_alias_by_prefix_or_sample_id(alias, prefix="name")


        # Step 3: mark all that left unmatched
        package.sample_aliases.filter(match_source__isnull=True).update(
            match_source=SampleAlias.MatchSource.NO_MATCH,
        )

        # mark all unused fastq files
        package_fastq: PackageSequencingData
        for package_fastq in package.assoc_sequencing_datas.filter(verdicts=[]):
            # TODO find more convenient way to separate used/not used fastqs
            package_fastq.add_verdict(
                "was not used in matching",
                package_fastq.VerdictLevel.WARNING,
            )

    def match_alias_by_prefix_or_sample_id(self, alias: SampleAlias, prefix="fastq_prefix"):
        """
        Handle sample alias that have fastq prefix.

        Validate, that all fastqs with such prefix either belong to same sample,
        or don't belong to a sample.

        If none of fastqs linked to a sample, create one from alias.
        After that, link all of these fastqs, and the alias, to the sample.

        2024-10: Second pass implemented, default is using the fastq_prefix
        Then we use the sample name to find matches.
        """
        package: Package = self.cleaned_data["package"]

        prefix_fastq_group = package.assoc_sequencing_datas.by_prefix(
            getattr(alias, prefix) + self.SAMPLE_PREFIX_DELIMITER,
        )

        if not prefix_fastq_group.exists():
            # validate that the package have at least one fastq with such prefix
            # We can proceed with matching with such type of error,
            # so we don't mark alias as no-matched
            alias.add_verdict(
                "No FASTQ files with such prefix provided",
                alias.VerdictLevel.WARNING,
            )
            alias.save()
            return

        fastq_count = prefix_fastq_group.count()
        if fastq_count not in (2, 4, 6):
            # We assume every fastq group should consist of 2,4 or 6 files.
            alias.add_verdict(
                f"Wrong FASTQ files count for a prefix: {fastq_count}",
                alias.VerdictLevel.ERROR,
            )
            package_fastq: PackageSequencingData
            for package_fastq in prefix_fastq_group:
                package_fastq.add_verdict(
                    f"Wrong FASTQ files count for a prefix: {fastq_count}",
                    package_fastq.VerdictLevel.ERROR,
                )
            return

        # ok, we have some fastqs for the alias.
        # check if members of the fastq group are linked to same (or no) sample
        distinct_samples_cnt = prefix_fastq_group.aggregate(
            cnt=Count("sequencing_data__sample", distinct=True),
        )["cnt"]

        if distinct_samples_cnt > 1:
            # We can't proceed with such type of error,
            # so we mark the alias as no-match
            alias.add_verdict(
                "Some of FASTQ files with such prefix point to different samples",
                alias.VerdictLevel.ERROR,
            )
            package_fastq: PackageSequencingData
            for package_fastq in prefix_fastq_group:
                package_fastq.add_verdict(
                    "Some of files with same prefix point to different samples",
                    package_fastq.VerdictLevel.ERROR,
                )

            alias.match_source = alias.MatchSource.NO_MATCH
            alias.save()
            return

        # As we made sure that there is no different samples for the group,
        # we can sync all members of the group to a single sample
        # if any of fastqs is associated with sample
        fastq_with_sample: PackageSequencingData = prefix_fastq_group.filter(
            sequencing_data__sample__isnull=False,
        ).first()

        if fastq_with_sample:
            # Sample found, use it
            seqdata: SequencingData = fastq_with_sample.sequencing_data
            sample: Sample = seqdata.sample
            if seqdata.data_location == seqdata.DataLocation.NCBI:
                # uploaded files were matched with already existing NCBI Sequencing Data
                match_source = SampleAlias.MatchSource.NCBI_FASTQ
            else:
                match_source = SampleAlias.MatchSource.FASTQ_UPLOADED
        else:
            # The whole group doesn't have a sample - we create one from alias.
            sample = Sample.objects.create(
                ncbi_taxon=Taxon.objects.first(),  # TODO what to put here?
                country=alias.country,
                sampling_date=alias.sampling_date,
                package=package,
            )
            match_source = SampleAlias.MatchSource.FASTQ_UPLOADED_NEW_SAMPLE

        # associate every sample-less fastq from the group with the sample
        fastqs_without_sample = prefix_fastq_group.filter(
            sequencing_data__sample__isnull=True,
        )
        package_fastq: PackageSequencingData
        for package_fastq in fastqs_without_sample:
            # TODO should we add sample directly to PackageSequencingData?
            # To be able to rollback changes when some of them are deleted?
            sample.sequencing_data_set.add(package_fastq.sequencing_data)

        for package_fastq in prefix_fastq_group:
            # update verdict on all fastq group, mark it as used in matching
            package_fastq.add_verdict(
                "was used in matching",
                package_fastq.VerdictLevel.INFO,
            )

        # finally, associate the alias with the sample
        self.associate_sample_and_alias(sample, alias, match_source)

    def match_alias_by_pattern(self, alias: SampleAlias):
        """
        Match sample aliases, which name follows NCBI naming patterns, by name.

        Mark such aliases as not matched if no match found at that stage.
        """
        biosample_origin_q = Sample.objects.filter(
            aliases__origin="BioSample",
            aliases__name__iexact=alias.name,
        ).order_by("-aliases__created_at")

        srs_origin_q = Sample.objects.filter(
            aliases__origin="SRS",
            aliases__name__iexact=alias.name,
        ).order_by("-aliases__created_at")

        seqdata_library_name_q = Sample.objects.filter(
            sequencing_data_set__library_name__iexact=alias.name,
        ).order_by("-sequencing_data_set__created_at")

        patterns = (
            (
                self.BIOSAMPLE_ORIGIN_PATTERN,
                biosample_origin_q,
                SampleAlias.MatchSource.NCBI,
            ),
            (
                self.SRS_ORIGIN_PATTERN,
                srs_origin_q,
                SampleAlias.MatchSource.NCBI,
            ),
            (
                self.LIBRARY_NAME_PATTERN,
                seqdata_library_name_q,
                SampleAlias.MatchSource.NCBI,
            ),
        )

        for pattern, query, match_source in patterns:
            if pattern.match(alias.name):
                matched_sample = query.first()
                if not matched_sample:
                    alias.add_verdict(
                        "Detected NCBI ID is not yet available, re-match later",
                        alias.VerdictLevel.ERROR,
                    )
                    alias.match_source = SampleAlias.MatchSource.NO_MATCH
                    alias.save()
                    return
                self.associate_sample_and_alias(matched_sample, alias, match_source)
                return

    def match_alias_by_name(self, alias: SampleAlias):
        """
        Perform match of alias with sample, using alias name.

        This is last stage of matching,
        for those aliases that haven't been matched at earlier stages.

        Search performed among NCBI/SRA aliases,
        then among FASTQ's library_name,
        then among user-uploaded aliases.
        """
        package: Package = self.cleaned_data["package"]

        ncbi_query = Sample.objects.filter(
            Q(aliases__package__origin__iexact="NCBI")
            | Q(
                aliases__package__origin__iexact="SRA",
            ),  # might be deprecated in future
            aliases__name__iexact=alias.name,
        ).order_by(
            "-aliases__created_at",
        )  # get latest

        fastq_libname_query = Sample.objects.filter(
            sequencing_data_set__library_name__iexact=alias.name,
        ).order_by(
            "-sequencing_data_set__created_at",
        )  # get latest

        user_aliases_query = Sample.objects.filter(
            aliases__package__owner=package.owner,
            # look only through accepted packages
            aliases__package__state=package.State.ACCEPTED,
            aliases__name__iexact=alias.name,
        ).order_by(
            "-aliases__created_at",
        )  # get latest

        queries = [
            # 1. By NCBI/SRA aliases name
            (ncbi_query, SampleAlias.MatchSource.NCBI),
            # 2. By FASTQ's library_name
            (fastq_libname_query, SampleAlias.MatchSource.FASTQ_EXISTING),
            # 3. By user-uploaded aliases name
            (user_aliases_query, SampleAlias.MatchSource.USER_ALIAS),
        ]

        for query, match_source in queries:
            matched_sample: Sample = query.first()
            if matched_sample:
                self.associate_sample_and_alias(matched_sample, alias, match_source)
                return

    def associate_sample_and_alias(
        self,
        sample: Sample,
        alias: SampleAlias,
        match_source: SampleAlias.MatchSource,
    ):
        """
        Shortcut for sample-alias associating procedure.

        Alias is being connected to the sample,
        and all alias-related mic/pds tests being updated with the sample.
        """
        alias.sample = sample
        alias.mic_tests.update(sample=sample)
        alias.pds_tests.update(sample=sample)
        alias.match_source = match_source
        alias.save()
