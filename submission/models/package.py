import logging
from typing import Any

from django import forms
from django.db import models
from django.db.models.functions import Upper
from django.utils import timezone
from django_fsm import FSMField, transition


from identity.models import User

log = logging.getLogger(__name__)


class RejectPackageForm(forms.Form):
    """Form, used in admin UI to specify reason when rejecting the package."""

    reason = forms.CharField(max_length=2048, min_length=4, widget=forms.Textarea)


class PackageQuerySet(models.QuerySet):
    """Custom queryset class for Package model."""

    def editable(self):
        """Filter states, on which package can be edited."""
        return self.filter(
            state__in=(
                Package.State.DRAFT,
                Package.State.REJECTED,
            ),
        )


class Package(models.Model):
    """
    Data submission package.

    Includes metadata and relations with corresponding input files.
    """

    objects: PackageQuerySet = PackageQuerySet.as_manager()

    class Meta:
        """Model options."""

        indexes = [
            # for iexact to work fast
            models.Index(Upper("origin"), name="package__origin__upper__idx"),
        ]

    class State(models.TextChoices):
        """Package state."""

        DRAFT = "DRAFT", "Draft"
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"
        UNSET = "", "Unset"

    class MatchingState(models.TextChoices):
        """Package matching state."""

        NEVER_MATCHED = "NEVER_MATCHED"
        """Package was never matched before."""
        MATCHED = "MATCHED"
        """Package was matched and hasn't changed since."""
        CHANGED = "CHANGED"
        """Package was matched and has changed since."""
        UNSET = ""

    submitted_on = models.DateTimeField(editable=False, default=timezone.now)
    state_changed_on = models.DateTimeField(default=timezone.now)

    name = models.CharField(blank=False, max_length=1024)
    description = models.CharField(max_length=8_192, blank=True, null=True)
    state = FSMField(choices=State.choices, default=State.DRAFT)
    origin = models.CharField(default="TBKB", max_length=1024)
    """Who started the package."""

    bioproject_id = models.BigIntegerField(null=True)

    owner = models.ForeignKey(User, models.SET_NULL, null=True, related_name="packages")

    matching_state = models.CharField(
        max_length=32,
        choices=MatchingState.choices,
        default=MatchingState.NEVER_MATCHED,
    )
    """Indicates current state of matching of the package."""

    rejection_reason = models.TextField(max_length=2048, default="")
    """Latest reason of package rejection (if any)."""

    sample_aliases: Any  # RelatedManager[SampleAlias]
    samples: Any  # RelatedManager[Sample]
    """Samples, created within the package."""
    mic_tests: Any  # RelatedManager[MICTest]
    pds_tests: Any  # RelatedManager[PDSTest]
    messages: Any  # RelatedManager[Message]
    contributors: Any  # RelatedManager[Contributor]
    attachments: Any  # RelatedManager[Attachment]
    # sequencing data M2M table
    assoc_sequencing_datas: Any  # RelatedManager[PackageSequencingData]
    # sequencing data
    sequencing_datas: Any  # RelatedManager[SequencingData]
    # one to one PackageStats
    stats: Any  # RelatedManager[PackageStats]

    def mark_changed(self):
        """
        Mark package as changed, if it was matched before.

        Also, if the package is being rejected when it is changed,
        it goes back to draft.
        Every time package is marked as changed,
        package stats are recalculated.
        """
        log.debug("updating package stats")
        self.stats.update()
        log.debug("package stats updated")

        if self.matching_state == self.MatchingState.MATCHED:
            self.matching_state = self.MatchingState.CHANGED
            self.save()

        if self.state == self.State.REJECTED:
            self.state = self.State.DRAFT
            self.save()

    def can_go_pending(self):
        """Package can go from draft to pending if not changed since last matching."""
        return self.matching_state == self.MatchingState.MATCHED

    @transition(
        field=state,
        source=(State.DRAFT, State.REJECTED),
        target=State.PENDING,
        conditions=[can_go_pending],
    )
    def to_pending(self):
        """After matching is done, user can send the package to pending action from admin."""

    @transition(field=state, source=State.PENDING, target=State.ACCEPTED)
    def pending_to_accepted(self):
        """
        After package is moderated by admin and all is good, package is accepted.

        All matched data inside the package being marked as ready for production (see app signals).
        """

    @transition(
        field=state,
        source=State.PENDING,
        target=State.REJECTED,
        custom={"form": RejectPackageForm, "short_description": "Reject with a reason"},
    )
    def pending_to_rejected(self, reason: str):
        """After package is moderated by admin and something is wrong, package is rejected."""
        self.rejection_reason = reason

    def __str__(self):
        """Represent instance of a package."""
        return f'<Package #{self.pk} "{self.name}">'
