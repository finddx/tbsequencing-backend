from django.db import models as m


class SummarySequencingStats(m.Model):
    """Summary sample sequencing stats model."""

    objects: m.Manager

    sample = m.OneToOneField("Sample", on_delete=m.CASCADE)

    median_depth = m.FloatField()
    coverage_10x = m.FloatField()
    coverage_15x = m.FloatField()
    coverage_20x = m.FloatField()
    coverage_30x = m.FloatField()

    raw_total_sequences = m.BigIntegerField()
    filtered_sequences = m.BigIntegerField()
    sequences = m.BigIntegerField()
    is_sorted = m.BigIntegerField()
    first_fragments = m.BigIntegerField()
    last_fragments = m.BigIntegerField()
    reads_mapped = m.BigIntegerField()
    reads_mapped_and_paired = m.BigIntegerField()
    reads_unmapped = m.BigIntegerField()
    reads_properly_paired = m.BigIntegerField()
    reads_paired = m.BigIntegerField()
    reads_duplicated = m.BigIntegerField()
    reads_mq_0 = m.BigIntegerField()
    reads_qc_failed = m.BigIntegerField()
    non_primary_alignments = m.BigIntegerField()
    total_length = m.BigIntegerField()
    total_first_fragment_length = m.BigIntegerField()
    total_last_fragment_length = m.BigIntegerField()
    bases_mapped = m.BigIntegerField()
    bases_mapped_cigar = m.BigIntegerField()
    bases_trimmed = m.BigIntegerField()
    bases_duplicated = m.BigIntegerField()
    mismatches = m.BigIntegerField()

    error_rate = m.FloatField()

    average_length = m.IntegerField()
    average_first_fragment_length = m.IntegerField()
    average_last_fragment_length = m.IntegerField()
    maximum_length = m.IntegerField()
    maximum_first_fragment_length = m.IntegerField()
    maximum_last_fragment_length = m.IntegerField()

    average_quality = m.FloatField()
    insert_size_average = m.FloatField()
    insert_size_standard_deviation = m.FloatField()

    inward_oriented_pairs = m.IntegerField()
    outward_oriented_pairs = m.IntegerField()
    pairs_with_other_orientation = m.IntegerField()
    pairs_on_different_chromosomes = m.IntegerField()

    percentage_of_properly_paired_reads = m.FloatField()
