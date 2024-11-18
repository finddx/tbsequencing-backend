# pylint: disable=duplicate-code

import pytest
from rest_framework.reverse import reverse

FILE_VALID = "pdst1__valid.xlsx"
FILE_VALID_2 = "pdst2__valid.xlsx"
FILE_VALID_3 = "pdst3__valid.xlsx"


@pytest.mark.parametrize(
    "filename",
    (FILE_VALID, FILE_VALID_2, FILE_VALID_3),
)
def test_upload_valid(
    client_of,
    package_of,
    alice,
    shared_datadir,
    filename,
    util,
    drugs,
    growth_mediums,
    countries,
    assessment_methods,
):  # pylint: disable=unused-argument,too-many-arguments
    """Successful upload redirects back to endpoint."""
    endpoint = reverse("v1:submission:pdstest-list", (package_of(alice).pk,))

    with open(shared_datadir / filename, "rb") as file:
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


def test_pdstest_clear_endpoint_302_response(package_of, client_of, alice, util):
    """PDS tests clear endpoint response redirects to PDS tests list."""
    clear_endpoint = reverse("v1:submission:pdstest-clear", (package_of(alice).pk,))
    package_endpoint = reverse("v1:submission:package-detail", (package_of(alice).pk,))

    # clear uploaded data
    response = client_of(alice).post(clear_endpoint, follow=False)
    assert response.status_code == 302
    assert response.headers["location"] == util.abs_uri(package_endpoint)


@pytest.mark.parametrize(
    "filename",
    (FILE_VALID, FILE_VALID_2),
)
def test_clear_pds_data(package_of, client_of, alice, shared_datadir, filename):
    """PDS tests are cleared along with attachments and aliases."""
    clear_endpoint = reverse("v1:submission:pdstest-clear", (package_of(alice).pk,))
    list_endpoint = reverse("v1:submission:pdstest-list", (package_of(alice).pk,))

    with open(shared_datadir / filename, "rb") as file:
        client_of(alice).post(
            list_endpoint,
            data={
                "file": file,
            },
        )

    # clear uploaded data
    client_of(alice).post(clear_endpoint, follow=False)

    assert package_of(alice).pds_tests.count() == 0
    assert package_of(alice).sample_aliases.count() == 0
    assert package_of(alice).attachments.count() == 0
