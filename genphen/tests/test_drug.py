from rest_framework.reverse import reverse

from genphen.models import Drug


def test_drug(client_of, alice, drugs):  # pylint: disable=unused-argument
    """Checking drug api with pagination."""
    endpoint = reverse("v1:genphen:drug-list")
    drug = Drug.objects.all().order_by("drug_name").first()
    response = client_of(alice).get(
        endpoint,
    )
    data = response.json()
    assert data[0]["drugId"] == drug.drug_id
    assert data[0]["drugName"] == drug.drug_name
    assert data[0]["code"] == drug.drug_code
    assert response.status_code == 200


def test_drug_detailed(client_of, alice, drug_of):
    """Checking global-sample api with detailed drug."""
    drug = drug_of("RIF", "Rifampicin")
    endpoint = reverse("v1:genphen:drug-detail", (drug.pk,))
    response = client_of(alice).get(
        endpoint,
    )
    data = response.json()
    assert data["drugId"] == drug.pk
    assert data["drugName"] == drug.drug_name
    assert data["code"] == drug.drug_code
    assert response.status_code == 200
