from rest_framework.reverse import reverse


def test_package_list_endpoint_200_response(package_of, alice, client_of, util):
    """Package list endpoint returns list of package data."""
    endpoint = reverse("v1:submission:package-list")
    package = package_of(alice)

    response = client_of(alice).get(endpoint)

    assert response.json() == [
        {
            "attachments": [],
            "contributors": util.abs_uri(
                reverse("v1:submission:contributor-list", (package.pk,)),
            ),
            "description": package.description,
            "matchingState": package.matching_state.value,
            "messages": util.abs_uri(
                reverse("v1:submission:message-list", (package.pk,)),
            ),
            "messagesCount": 0,
            "micDrugs": [],
            "micDrugsCount": 0,
            "micTests": util.abs_uri(
                reverse("v1:submission:mictest-list", (package.pk,)),
            ),
            "micTestsCount": 0,
            "name": package.name,
            "origin": package.origin,
            "pdsDrugConcentrationCount": 0,
            "pdsDrugs": [],
            "pdsDrugsCount": 0,
            "pdsTests": util.abs_uri(
                reverse("v1:submission:pdstest-list", (package.pk,)),
            ),
            "pdsTestsCount": 0,
            "pk": package.pk,
            "rejectionReason": package.rejection_reason,
            "sampleAliases": util.abs_uri(
                reverse("v1:submission:samplealias-list", (package.pk,)),
            ),
            "sampleAliasesCount": 0,
            "sequencingData": util.abs_uri(
                reverse("v1:submission:packagesequencingdata-list", (package.pk,)),
            ),
            "sequencingDataCount": 0,
            "state": package.state.value,
            "stateChangedOn": util.ftime(package.state_changed_on),
            "url": util.abs_uri(reverse("v1:submission:package-detail", (package.pk,))),
        },
    ]


def test_package_detail_endpoint_200_response(package_of, alice, client_of, util):
    """Package detail endpoint returns package data."""
    endpoint = reverse("v1:submission:package-detail", (package_of(alice).pk,))

    response = client_of(alice).get(endpoint)

    assert response.json() == {
        "attachments": [],
        "contributors": util.abs_uri(
            reverse("v1:submission:contributor-list", (package_of(alice).pk,)),
        ),
        "description": "Alice Aliceson empty from the start submission package",
        "matchingState": "NEVER_MATCHED",
        "messages": util.abs_uri(
            reverse("v1:submission:message-list", (package_of(alice).pk,)),
        ),
        "messagesCount": 0,
        "micDrugs": [],
        "micDrugsCount": 0,
        "micTests": util.abs_uri(
            reverse("v1:submission:mictest-list", (package_of(alice).pk,)),
        ),
        "micTestsCount": 0,
        "name": "Alice empty package",
        "origin": "TBKB",
        "pdsDrugConcentrationCount": 0,
        "pdsDrugs": [],
        "pdsDrugsCount": 0,
        "pdsTests": util.abs_uri(
            reverse("v1:submission:pdstest-list", (package_of(alice).pk,)),
        ),
        "pdsTestsCount": 0,
        "pk": package_of(alice).pk,
        "rejectionReason": "",
        "sampleAliases": util.abs_uri(
            reverse("v1:submission:samplealias-list", (package_of(alice).pk,)),
        ),
        "sampleAliasesCount": 0,
        "sequencingData": util.abs_uri(
            reverse(
                "v1:submission:packagesequencingdata-list",
                (package_of(alice).pk,),
            ),
        ),
        "sequencingDataCount": 0,
        "state": "DRAFT",
        "stateChangedOn": util.ftime(package_of(alice).state_changed_on),
        "url": util.abs_uri(endpoint),
    }


def test_package_match_endpoint_302_response(
    package_of,
    alice,
    client_of,
    new_alias_of,
    util,
):
    """Successful package match response redirects to package details endpoint."""
    package = package_of(alice)
    new_alias_of(package, "A1")  # to make package non-empty

    response = client_of(alice).post(
        reverse("v1:submission:package-match", (package.pk,)),
        follow=False,
    )
    assert response.status_code == 302
    assert response.headers["location"] == util.abs_uri(
        reverse("v1:submission:package-detail", (package.pk,)),
    )


def test_package_submit_endpoint_302_response(
    package_of,
    client_of,
    alice,
    util,
):
    """Package submit response redirects to package details endpoint."""
    package = package_of(alice)
    # we can submit only matched package
    package.matching_state = package.MatchingState.MATCHED
    package.save()

    response = client_of(alice).post(
        reverse("v1:submission:package-submit", (package.pk,)),
        follow=False,
    )

    assert response.status_code == 302
    assert response.headers["location"] == util.abs_uri(
        reverse("v1:submission:package-detail", (package.pk,)),
    )


def test_package_create_endpoint(client_of, alice, util):
    """Create a package."""
    response = client_of(alice).post(
        reverse("v1:submission:package-list"),
        data={
            "name": "The package",
            "description": "The package description",
        },
    )

    package = alice.packages.first()
    assert package.name == "The package"
    assert package.description == "The package description"
    assert response.status_code == 201
    assert response.headers["location"] == util.abs_uri(
        reverse("v1:submission:package-detail", (package.pk,)),
    )
