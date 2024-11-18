from rest_framework.reverse import reverse


def test_get_aliases_list(client_of, alice, package_of, new_alias_of):
    """Sample aliases data is returned, ordered by alias name."""
    a_1 = new_alias_of(package_of(alice), "A1")
    a_2 = new_alias_of(package_of(alice), "A2")

    response = client_of(alice).get(
        reverse("v1:submission:samplealias-list", (package_of(alice).pk,)),
    )

    assert response.json() == [
        {
            "fastqPrefix": None,
            "matchSource": None,
            "micTestsCount": 0,
            "name": a_1.name,
            "pdsTestsCount": 0,
            "pk": a_1.pk,
            "verdicts": [],
        },
        {
            "fastqPrefix": None,
            "matchSource": None,
            "micTestsCount": 0,
            "name": a_2.name,
            "pdsTestsCount": 0,
            "pk": a_2.pk,
            "verdicts": [],
        },
    ]


def test_alias_name_update(client_of, alice, package_of, new_alias_of):
    """Alias name updated."""
    package = package_of(alice)
    a_1 = new_alias_of(package, "A1")
    new_name = "T9"

    response = client_of(alice).put(
        reverse("v1:submission:samplealias-detail", (package.pk, a_1.pk)),
        data={
            "name": new_name,
        },
    )
    assert response.json() == {
        "fastqPrefix": None,
        "matchSource": None,
        "micTestsCount": 0,
        "name": new_name,
        "pdsTestsCount": 0,
        "pk": a_1.pk,
        "verdicts": [],
    }
    a_1.refresh_from_db()
    assert a_1.name == new_name


def test_alias_name_update_resets_verdicts(client_of, alice, package_of, new_alias_of):
    """Alias name update resets alias verdicts."""
    package = package_of(alice)
    a_1 = new_alias_of(package, "A1")
    a_1.add_verdict("Info verdict", a_1.VerdictLevel.INFO)
    a_1.add_verdict("Error verdict", a_1.VerdictLevel.ERROR)
    a_1.refresh_from_db()
    assert len(a_1.verdicts) == 2

    new_name = "HT"

    response = client_of(alice).put(
        reverse("v1:submission:samplealias-detail", (package.pk, a_1.pk)),
        data={
            "name": new_name,
        },
    )
    assert response.json() == {
        "fastqPrefix": None,
        "matchSource": None,
        "micTestsCount": 0,
        "name": new_name,
        "pdsTestsCount": 0,
        "pk": a_1.pk,
        "verdicts": [],
    }
    a_1.refresh_from_db()
    assert len(a_1.verdicts) == 0


def test_update_alias_name_forbid_existing(client_of, alice, package_of, new_alias_of):
    """Can't update alias name on already existing name. Case-insensitive."""
    package = package_of(alice)
    a_1 = new_alias_of(package, "A1")
    b_2 = new_alias_of(package, "B2")

    response = client_of(alice).put(
        reverse("v1:submission:samplealias-detail", (package.pk, a_1.pk)),
        data={
            "name": b_2.name.lower(),
        },
    )
    assert response.json() == {
        "errors": [
            {
                "attr": "name",
                "code": "invalid",
                "detail": "Such sample name already exists.",
            },
        ],
        "type": "validation_error",
    }
