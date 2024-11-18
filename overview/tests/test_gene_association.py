from rest_framework.reverse import reverse

from overview.models import DrugGene


def test_gene_association(client_of, alice):
    """Checking gene_association api with related drugs."""
    endpoint = reverse("v1:overview:gene-association-list")
    response = client_of(alice).get(
        endpoint,
    )
    data = response.json()
    gene_association = (
        DrugGene.objects.all()
        .values("gene_db_crossref", "gene_name")
        .distinct(
            "gene_db_crossref",
        )
    )
    results = []
    if gene_association:
        for gene in gene_association:
            gene["drugs"] = DrugGene.objects.filter(gene_name=gene["gene_name"]).values(
                "drug",
                "drug_name",
            )
            results.append(gene)
        assert len(data) == len(results)
    assert response.status_code == 200


def test_gene_association_detailed(client_of, alice):
    """Checking gene_association api detailed by one gene with it's related drugs."""
    gene_association = DrugGene.objects.all().values("gene_name", "drug", "drug_name")
    if gene_association:
        gene_association_detailed = gene_association.first()
        instances = DrugGene.objects.filter(
            gene_name=gene_association_detailed["gene_name"],
        ).values("drug", "drug_name")
        endpoint = reverse(
            "gene-association-detail",
            (gene_association_detailed["drug"],),
        )
        response = client_of(alice).get(
            endpoint,
        )
        data = response.json()
        assert data["geneName"] == gene_association_detailed["gene_name"]
        assert len(data["drugs"]) == len(instances)
        assert response.status_code == 200
