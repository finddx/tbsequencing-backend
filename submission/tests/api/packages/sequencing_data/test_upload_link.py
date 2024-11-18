from unittest.mock import MagicMock

from rest_framework.reverse import reverse


def test_get_upload_link_for_fresh_file(package_of, client_of, alice, s3_stub, mocker):
    """Upload link obtained, if no such file already uploaded on S3 by the user."""
    endpoint = reverse(
        "v1:submission:packagesequencingdata-uploadlink",
        (package_of(alice).pk,),
    )
    mocked_url = "https://aws.com/presigned-url"

    # permanent location check mock
    mocker.patch(
        "submission.services.s3bucket.FastqPermanentStorage.exists",
        return_value=False,
    )
    # tmp location check mock
    mocker.patch(
        "submission.services.s3bucket.FastqTMPStorage.exists",
        return_value=False,
    )
    # generate link mock
    s3_stub.client.generate_presigned_url = MagicMock(return_value=mocked_url)

    response = client_of(alice).post(
        endpoint,
        {
            "filename": "file.fastq.gz",
        },
    )

    assert response.json() == {"url": mocked_url}


def test_error_obtaining_upload_link_for_tmp_uploaded_file(
    package_of,
    client_of,
    alice,
    mocker,
):
    """Cannot obtain link for file, that is already on TMP location."""
    endpoint = reverse(
        "v1:submission:packagesequencingdata-uploadlink",
        (package_of(alice).pk,),
    )

    # permanent location check mock
    mocker.patch(
        "submission.services.s3bucket.FastqPermanentStorage.exists",
        return_value=False,
    )
    # tmp location check mock
    mocker.patch(
        "submission.services.s3bucket.FastqTMPStorage.exists",
        return_value=True,
    )

    response = client_of(alice).post(
        endpoint,
        {
            "filename": "file.fastq.gz",
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        "errors": [
            {
                "attr": None,
                "code": "conflict",
                "detail": "file is already uploaded, proceed to fetch directly.",
            },
        ],
        "type": "client_error",
    }
