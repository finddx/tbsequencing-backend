from rest_framework import serializers

from ..models import GeneSearchHistory


class GeneSearchSerializer(serializers.Serializer):  # pylint: disable=W0223
    """Gene recently searched data, read serializer."""

    counter = serializers.IntegerField()
    gene_name = serializers.SerializerMethodField()
    gene_db_crossref_id = serializers.IntegerField()
    locus_tag = serializers.SerializerMethodField()
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    def get_gene_name(self, obj: GeneSearchHistory):
        """Get gene_name from Gene view."""
        return obj.gene_db_crossref.data.gene_name

    def get_locus_tag(self, obj: GeneSearchHistory):
        """Get locus_tag from Gene view."""
        return obj.gene_db_crossref.data.locus_tag
