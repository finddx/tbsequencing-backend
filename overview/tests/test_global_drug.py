from rest_framework.reverse import reverse

from overview.models import SampleDrugResultStats, SampleDrugResult


def test_pheno_resistance_by_drug(
    client_of,
    alice,
    alice_package,
    drugs,
    countries,
):
    """Phenotypic resistance stats, counted by stats."""
    inh, rif, *_ = drugs
    for drug, test_result in zip((rif, rif, inh, inh, inh), "SRRRR"):
        alice_package.new_sample(countries[0].three_letters_code, 2022)
        alice_package.new_alias(str(alice_package.sample.id), alice_package.sample)
        alice_package.new_pds_test(test_result, drug=drug, staging=False)

    SampleDrugResult.refresh()
    SampleDrugResultStats.refresh()

    endpoint = reverse("v1:overview:global-drug-list")
    response = client_of(alice).get(
        endpoint,
        data={"yearGte": "2022", "resistanceType": "Pheno"},
    )
    data = response.json()
    assert data == [
        {
            "drug": inh.drug_id,
            "intermediate": 0,
            "ratioIntermediate": "0.0",
            "ratioResistant": "100.0",
            "ratioSusceptible": "0.0",
            "resistant": 3,
            "susceptible": 0,
            "total": 3,
        },
        {
            "drug": rif.drug_id,
            "intermediate": 0,
            "ratioIntermediate": "0.0",
            "ratioResistant": "50.0",
            "ratioSusceptible": "50.0",
            "resistant": 1,
            "susceptible": 1,
            "total": 2,
        },
    ]


# pylint: disable=unused-variable,too-many-locals
def test_pheno_resistance_by_country(client_of, alice, alice_package, countries, drugs):
    """Phenotypic resistance stats, counted by country."""
    abw, fra, kaz, *_ = countries
    inh, rif, *_ = drugs
    for country, year, drug, test_result in zip(
        (fra, fra, fra, kaz, kaz, kaz),
        (2020,) * 6,
        (rif, rif, inh, inh, inh, inh),
        "SRRIII",
    ):
        alice_package.new_sample(country.three_letters_code, year)
        alice_package.new_alias(str(alice_package.sample.id), alice_package.sample)
        alice_package.new_pds_test(test_result, drug=drug, staging=False)

    SampleDrugResult.refresh()
    SampleDrugResultStats.refresh()

    endpoint = reverse("v1:overview:global-drug-map-list")
    response = client_of(alice).get(
        endpoint,
        data={"countryID": "FRA", "resistanceType": "Pheno"},
    )
    data = response.json()
    assert data == [
        {
            "countryId": "FRA",
            "intermediate": 0,
            "ratioIntermediate": "0.0",
            "ratioResistant": "66.7",
            "ratioSusceptible": "33.3",
            "resistant": 2,
            "susceptible": 1,
            "total": 3,
        },
    ]
