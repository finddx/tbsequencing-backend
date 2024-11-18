from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, serializers
from rest_framework.generics import get_object_or_404

from genphen.models import GeneDrugResistanceAssociation
from genphen.serializers import DrugReadSerializer


# TODO remove together with DrugGene matview after FE switched on new endpoint


class LegacyGeneDrugResistanceAssociationSerializer(serializers.ModelSerializer):
    """Legacy gene drug resistance association serializer."""

    gene_db_crossref = serializers.IntegerField(source="gene_db_crossref_id")
    gene_name = serializers.SerializerMethodField()
    drugs = serializers.SerializerMethodField()

    def get_gene_name(self, obj: GeneDrugResistanceAssociation):
        """Forward gene name from overview_gene matview."""
        return obj.gene_db_crossref.data.gene_name

    def get_drugs(self, obj: GeneDrugResistanceAssociation):
        """Show all drugs, that the gene is associated with (tier ignored)."""
        drugs = []
        drugs_queryset = (
            obj.gene_db_crossref.drug_resistance_associations.select_related(
                "drug",
            ).distinct("drug")
        )
        for gdra in drugs_queryset:
            drugs.append(
                DrugReadSerializer(gdra.drug).data,
            )
        return drugs

    class Meta:
        """Meta class."""

        model = GeneDrugResistanceAssociation
        fields = (
            "gene_db_crossref",
            "gene_name",
            "drugs",
        )


class GeneAssociationViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
):
    """
    Legacy gene drug resistance associations viewset.

    Must be switched to GeneDrugResistanceAssociationsViewSet (FE work required).
    """

    queryset = (
        GeneDrugResistanceAssociation.objects.distinct("gene_db_crossref")
        .select_related("gene_db_crossref__data")
        .select_related("drug")
#        .filter(gene_db_crossref__data__gene_name__isnull=False)
        .order_by("gene_db_crossref")
        .all()
    )
    serializer_class = LegacyGeneDrugResistanceAssociationSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ["drug"]

    def get_object(self):
        """Retrieve single object by gene db crossref id."""
        return get_object_or_404(
            self.queryset.filter(gene_db_crossref=self.kwargs.get("pk")),
        )
