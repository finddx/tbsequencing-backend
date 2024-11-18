from rest_framework.reverse import reverse


def test_drug_gene_info_with_pagination(
    client_of,
    alice,
    annotations,
):  # pylint: disable=unused-argument
    """Checking drug-gene-info api for pagination and ordering."""
    # pylint: disable=unused-variable

    endpoint_order = reverse("v1:overview:drug-gene-infos-list")
    response = client_of(alice).get(
        endpoint_order,
        data={"paginated": "true", "order": "-globalFrequency", "pageSize": 1},
    )
    data = response.json()

    assert data["count"] == 2
    assert data["previous"] is None
    assert (
        data["next"] == "http://testserver/api/v1/overview/drug-gene-infos/"
        "?order=-globalFrequency&page=2&pageSize=1&paginated=true"
    )
    result = data["results"][0]
    assert result["geneDbCrossrefId"] == 10
    assert result["geneName"] == "Rv0004"
    assert result["variantName"] == "2160001-TAGA-GTAA"
    assert result["nucleodicAnnName"] == "AAA"
    assert result["proteicAnnName"] == "BBB"
    assert result["consequence"] == "UPSTREAM"
    assert result["resistantCount"] == 0
    assert result["susceptbleCount"] == 10
    assert result["intermediateCount"] == 0
    assert result["globalFrequency"] == "50.00"
    assert result["totalCounts"] == 10
    assert result["startPos"] == 4434 + 78
    assert result["endPos"] == 4997 + 78


def test_drug_gene_info_without_pagination(
    client_of,
    alice,
    annotations,  # pylint: disable=unused-argument
):
    """Checking drug-gene-info api for searching by any field and ordering."""
    endpoint_order = reverse("v1:overview:drug-gene-infos-list")
    response_order = client_of(alice).get(
        endpoint_order,
        data={"order": "totalCounts"},
    )
    data = response_order.json()
    assert isinstance(data, list)
    assert len(data) == 2

    assert data[0]["variantName"] == "2160001-TAGA-GTAA"
    assert data[1]["variantName"] == "2160002-TAGA-GTAA"
