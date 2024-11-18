from rest_framework.reverse import reverse

from overview.models import Gene, DrugGene


def test_gene(client_of, alice):
    """Checking gene api with pagination."""
    endpoint = reverse("v1:overview:gene-list")
    response = client_of(alice).get(
        endpoint,
    )
    data = response.json()
    assert data["count"] == Gene.objects.all().count()
    assert data["previous"] is None
    assert data["next"] == "http://testserver/api/v1/overview/genes/?page=2"
    assert response.status_code == 200


def test_gene_search(client_of, alice):
    """Checking gene api by searching."""
    gene = (
        Gene.objects.all()
        .values(
            "ncbi_id",
            "strand",
            "locus_tag",
            "end_pos",
            "gene_name",
            "gene_db_crossref",
            "start_pos",
        )
        .order_by("gene_db_crossref")
    )
    gene_name = gene[0]["gene_name"]
    locus_tag = gene[0]["locus_tag"]
    end_pos = gene[0]["end_pos"]

    endpoint = reverse("v1:overview:gene-list")
    response = client_of(alice).get(
        endpoint,
        data={"search": gene_name},
    )
    data = response.json()
    assert data["results"][0]["geneName"] == gene_name
    assert data["results"][0]["locusTag"] == locus_tag
    assert data["results"][0]["endPos"] == end_pos
    assert response.status_code == 200


def test_gene_detailed(client_of, alice):
    """Checking gene api with detailed gene."""
    gene = (
        Gene.objects.all()
        .values(
            "start_pos",
            "end_pos",
            "gene_db_crossref",
            "gene_name",
            "locus_tag",
            "ncbi_id",
            "strand",
        )
        .order_by("gene_db_crossref")
    )
    gene_db_crossref = gene[0]["gene_db_crossref"]
    gene_name = gene[0]["gene_name"]
    drug_gene_associated = DrugGene.objects.filter(
        gene_db_crossref=gene_db_crossref,
    ).values("gene_name", "drug", "drug_name")

    endpoint = reverse("v1:overview:gene-detail", (gene_db_crossref,))
    response = client_of(alice).get(
        endpoint,
    )
    data = response.json()
    if drug_gene_associated:
        counter = drug_gene_associated.count()
        assert len(data["genes"][gene_name]) == counter
    assert data["genesOverview"]["geneDbCrossrefId"] == gene_db_crossref
    assert data["genesOverview"]["geneName"] == gene_name
    assert response.status_code == 200


def test_gene_genome(client_of, alice):
    """Checking drug api by genome-context with ordering of start positions."""
    endpoint = reverse("v1:overview:gene-genomecontext")
    response = client_of(alice).get(
        endpoint,
        data={"startPos": 100000, "endPos": 200000},
    )
    data = response.json()
    if len(data) >= 2:
        assert data[0]["startPos"] <= data[1]["startPos"]
        assert data[0]["endPos"] <= data[-1]["endPos"]
    assert response.status_code == 200
