from rest_framework.reverse import reverse


def test_create_contributors(client_of, package_of, alice, util):
    """Create multiple contributors at once."""
    endpoint = reverse("v1:submission:contributor-list", (package_of(alice).pk,))

    response = client_of(alice).post(
        endpoint,
        data={
            "contributors": [
                {
                    "firstName": "Ann",
                    "lastName": "Smith",
                    "role": "Head of lab",
                },
                {
                    "firstName": "John",
                    "lastName": "Smith",
                    "role": "Scientist",
                },
            ],
        },
        format="json",
    )

    contributors = package_of(alice).contributors.all()

    assert response.status_code == 201
    assert response.json() == {
        "contributors": [
            {
                "pk": contributors[0].pk,
                "url": util.abs_uri(
                    reverse(
                        "v1:submission:contributor-detail",
                        (package_of(alice).pk, contributors[0].pk),
                    ),
                ),
                "firstName": "Ann",
                "lastName": "Smith",
                "role": "Head of lab",
            },
            {
                "pk": contributors[1].pk,
                "url": util.abs_uri(
                    reverse(
                        "v1:submission:contributor-detail",
                        (package_of(alice).pk, contributors[1].pk),
                    ),
                ),
                "firstName": "John",
                "lastName": "Smith",
                "role": "Scientist",
            },
        ],
    }


def test_list_contributors(client_of, package_of, alice, util):
    """Validate contributors list."""
    endpoint = reverse("v1:submission:contributor-list", (package_of(alice).pk,))

    contributors = []
    for fname, lname, role in ("Ann Smith Role1".split(), "John Smith Role2".split()):
        contributor = package_of(alice).contributors.create(
            first_name=fname,
            last_name=lname,
            role=role,
        )
        contributors.append(contributor)

    response = client_of(alice).get(endpoint)

    assert response.status_code == 200
    assert response.json() == [
        {
            "pk": contributors[0].pk,
            "url": util.abs_uri(
                reverse(
                    "v1:submission:contributor-detail",
                    (package_of(alice).pk, contributors[0].pk),
                ),
            ),
            "firstName": "Ann",
            "lastName": "Smith",
            "role": "Role1",
        },
        {
            "pk": contributors[1].pk,
            "url": util.abs_uri(
                reverse(
                    "v1:submission:contributor-detail",
                    (package_of(alice).pk, contributors[1].pk),
                ),
            ),
            "firstName": "John",
            "lastName": "Smith",
            "role": "Role2",
        },
    ]
