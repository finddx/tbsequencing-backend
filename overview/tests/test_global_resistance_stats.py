from rest_framework.reverse import reverse

from overview.models import GlobalResistanceStats


def test_endpoint_response(client_of, alice, new_sample):
    """Global resistance stats endpoint response format is still."""
    endpoint = reverse("v1:overview:global-resistance-stats")
    _, _ = new_sample(), new_sample()
    GlobalResistanceStats.refresh()

    response = client_of(alice).get(endpoint)
    data = response.json()
    assert data == {
        "countries": [],
        "total": {
            "extDrugResSum": 0,
            "monoResSum": 0,
            "multiDrugResSum": 0,
            "polyResSum": 0,
            "ratioExtDrugRes": 0.0,
            "ratioMonoRes": 0.0,
            "ratioMultiDrugRes": 0.0,
            "ratioPolyRes": 0.0,
            "ratioRifRes": 0.0,
            "rifResSum": 0,
            "totalSum": 2,
        },
    }
