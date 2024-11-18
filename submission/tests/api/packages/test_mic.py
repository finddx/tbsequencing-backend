from rest_framework.reverse import reverse

MIC_VALID = "mic_valid.xlsx"


def test_successful_upload_redirects_back(
    client_of,
    package_of,
    alice,
    shared_datadir,
    util,
    drugs,
    countries,
):  # pylint: disable=unused-argument,too-many-arguments
    """Successful upload redirects back to endpoint."""
    endpoint = reverse("v1:submission:mictest-list", (package_of(alice).pk,))
    with open(shared_datadir / MIC_VALID, "rb") as file:
        response = client_of(alice).post(
            endpoint,
            data={
                "file": file,
            },
            follow=False,
        )
    assert response.status_code == 302, response.json()
    assert response.headers["location"] == util.abs_uri(
        reverse(
            "v1:submission:package-detail",
            (package_of(alice).pk,),
        ),
    )


def test_mictest_clear_endpoint_302_response(package_of, client_of, alice, util):
    """MIC tests clear endpoint response redirects to MIC tests list."""
    clear_endpoint = reverse("v1:submission:mictest-clear", (package_of(alice).pk,))
    package_endpoint = reverse("v1:submission:package-detail", (package_of(alice).pk,))

    # clear uploaded data
    response = client_of(alice).post(clear_endpoint, follow=False)
    assert response.status_code == 302
    assert response.headers["location"] == util.abs_uri(package_endpoint)
