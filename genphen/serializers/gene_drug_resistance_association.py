from rest_framework import serializers
from ..models import GeneDrugResistanceAssociation


class GeneDrugResistanceAssociationSerializer(serializers.ModelSerializer):
    """Gene drug resistance association serializer."""

    gene_name = serializers.SerializerMethodField()
    locus_tag = serializers.SerializerMethodField()

    def get_gene_name(self, obj):
        """Forward gene name from overview_gene matview."""
        return obj.gene_db_crossref.data.gene_name

    def get_locus_tag(self, obj):
        """Get locus_tag from Gene view."""
        return obj.gene_db_crossref.data.locus_tag

    class Meta:
        """Meta class."""

        model = GeneDrugResistanceAssociation
        fields = (
            "drug_id",
            "gene_db_crossref_id",
            "locus_tag",
            "gene_name",
            "tier",
        )
