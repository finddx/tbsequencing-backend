from rest_framework import serializers


class GeneDrugStatsSerializer(serializers.Serializer):  # pylint: disable=W0223
    """Drug and gene info retrieving serializer."""

    drug = serializers.IntegerField()
    drug_name = serializers.CharField(source="drug__drug_name")
    gene_db_crossref_id = serializers.IntegerField(source="gene_db_crossref")
    gene_name = serializers.CharField(read_only=True)
    variant_name = serializers.CharField(read_only=True)
    variant_grade = serializers.CharField(read_only=True)
    variant_grade_version = serializers.IntegerField(read_only=True)
    nucleodic_ann_name = serializers.CharField(read_only=True)
    proteic_ann_name = serializers.CharField(read_only=True)
    consequence = serializers.CharField(read_only=True)
    resistant_count = serializers.IntegerField()
    # historical typo, keep
    susceptble_count = serializers.IntegerField(source="susceptible_count")
    intermediate_count = serializers.IntegerField()
    global_frequency = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_counts = serializers.IntegerField()
    start_pos = serializers.IntegerField()
    end_pos = serializers.IntegerField()
