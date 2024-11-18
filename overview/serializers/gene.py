from rest_framework import serializers

from overview.models import Gene


class GeneSerializer(serializers.ModelSerializer):  # pylint: disable=abstract-method
    """Gene model serializer."""

    gene_db_crossref_id = serializers.IntegerField(source="dbxref_id")

    class Meta:
        """Gene model serializer options."""

        model = Gene
        fields = (
            "gene_name",
            "gene_db_crossref_id",
            "locus_tag",
            "ncbi_id",
            "gene_description",
            "gene_type",
            "start_pos",
            "strand",
            "end_pos",
            "protein_length",
        )


# pylint: disable=abstract-method
class GeneRetrieveSerializer(serializers.Serializer):
    """Gene retrieve serializer."""

    genes_overview = GeneSerializer(read_only=True, source="*")
    genes = serializers.SerializerMethodField(read_only=True)

    def get_genes(self, obj: Gene):
        """Preserve legacy response structure."""
        gene_name = obj.gene_name
        gene_drugs = list(
            {
                gdra.drug.drug_name
                for gdra in obj.dbxref.drug_resistance_associations.all()
            },
        )
        return {gene_name: gene_drugs}
