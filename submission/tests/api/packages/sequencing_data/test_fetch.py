import uuid

from rest_framework.reverse import reverse

VALID_FILE_NAME = "valid.fastq.gz"
INVALID_FILE = "invalid.fastq.gz"


def test_validate_uploaded_file(
    package_of,
    client_of,
    alice,
    shared_datadir,
    mocker,
):  # pylint: disable=too-many-arguments
    """
    S3 uploaded file fetched from TMP and validated successfully.

    SequencingData object created respectively.
    File moved to FINAL location.
    """
    endpoint = reverse(
        "v1:submission:packagesequencingdata-fetch",
        (package_of(alice).pk,),
    )
    filename = "anything.fastq.gz"

    # in order to not actually move the file inside S3
    persist_mock = mocker.patch(
        "submission.views.sequencing_data.SequencingDataS3BucketService.persist_file",
    )
    # to not actually remove tmp file from S3
    mocker.patch(
        "submission.views.sequencing_data.SequencingDataS3BucketService.remove_tmp_file",
    )
    mocker.patch(
        "submission.services.s3bucket.FastqTMPStorage.exists",
        return_value=True,
    )

    with open(shared_datadir / VALID_FILE_NAME, "rb") as body:
        mocker.patch(
            "submission.util.storage.FastqStorage.open",
            mocker.mock_open(read_data=body.read()),
        )
        uuid_name = uuid.uuid4()
        mocker.patch("submission.services.s3bucket.uuid.uuid4", return_value=uuid_name)

        response = client_of(alice).post(endpoint, {"filename": filename})

    obj = package_of(alice).sequencing_datas.first()
    full_filename = f"{uuid_name.hex}.{filename.split('.', 1)[1]}"
    assert obj.filename == full_filename
    assert obj.file_path == f"persistent/{full_filename}"
    assert obj.data_location == "TB-Kb"
    assert obj.hashes.count() == 1

    persist_mock.assert_called_once()

    # redirect to newly created SequencingData object
    assert response.status_code == 302


def test_failed_validate_uploaded_file(
    package_of,
    client_of,
    alice,
    shared_datadir,
    mocker,
):  # pylint: disable=too-many-arguments
    """S3 file does not pass validation, and deleted from TMP."""
    endpoint = reverse(
        "v1:submission:packagesequencingdata-fetch",
        (package_of(alice).pk,),
    )
    filename = "anything.fastq.gz"

    mocker.patch(
        "submission.services.s3bucket.FastqTMPStorage.exists",
        return_value=True,
    )
    remove_tmp_mock = mocker.patch(
        "submission.views.sequencing_data.SequencingDataS3BucketService.remove_tmp_file",
    )

    with open(shared_datadir / INVALID_FILE, "rb") as body:
        mocker.patch(
            "submission.util.storage.FastqStorage.open",
            mocker.mock_open(read_data=body.read()),
        )

        response = client_of(alice).post(endpoint, {"filename": filename})

    remove_tmp_mock.assert_called_once()
    assert response.status_code == 400
    assert response.json() == {
        "errors": [
            {
                "attr": "uploadedFile",
                "code": "invalid",
                "detail": "Lengths of sequence and quality values differs for "
                "SRR19739149.1.1 1 length=4 (4 and 5).",
            },
        ],
        "type": "validation_error",
    }
