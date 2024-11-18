from rest_framework.reverse import reverse

from submission.models import SequencingData


def test_get_sequencing_data_list(alice, client_of, package_of, mocker, util):
    """Validate package sequencing data list."""
    for i in range(2):
        fastq = SequencingData.objects.create(
            data_location=f"anywhere{i}",
            library_name=f"whatever{i}",
        )
        fastq_hash = fastq.hashes.create(
            algorithm="MD5",
            value="1234ff",
        )
        package_of(alice).assoc_sequencing_datas.create(
            sequencing_data=fastq,
            sequencing_data_hash=fastq_hash,
            filename=f"{i}.fastq.gz",
        )

    # we need to mock file url because we don't test with aws file backend
    mocker.patch(
        "submission.serializers.sequencing_data.SequencingDataSerializer.get_file_url",
        return_value="s3://whatever",
    )

    endpoint = reverse(
        "v1:submission:packagesequencingdata-list",
        (package_of(alice).pk,),
    )
    fastqs = package_of(alice).assoc_sequencing_datas.all()

    response = client_of(alice).get(endpoint)

    assert response.status_code == 200
    assert response.json() == [
        {
            "createdAt": util.ftime(fastqs[0].created_at),
            "filename": "0.fastq.gz",
            "pk": fastqs[0].pk,
            "sequencingData": {
                "dataLocation": "anywhere0",
                "filePath": None,
                "fileSize": None,
                "fileUrl": "s3://whatever",
                "filename": "",
                "libraryName": "whatever0",
                "pk": fastqs[0].sequencing_data.pk,
            },
            "url": util.abs_uri(
                reverse(
                    "v1:submission:packagesequencingdata-detail",
                    (package_of(alice).pk, fastqs[0].pk),
                ),
            ),
            "verdicts": [],
        },
        {
            "createdAt": util.ftime(fastqs[1].created_at),
            "filename": "1.fastq.gz",
            "pk": fastqs[1].pk,
            "sequencingData": {
                "dataLocation": "anywhere1",
                "filePath": None,
                "fileSize": None,
                "fileUrl": "s3://whatever",
                "filename": "",
                "libraryName": "whatever1",
                "pk": fastqs[1].sequencing_data.pk,
            },
            "url": util.abs_uri(
                reverse(
                    "v1:submission:packagesequencingdata-detail",
                    (package_of(alice).pk, fastqs[1].pk),
                ),
            ),
            "verdicts": [],
        },
    ]


def test_delete_package_fastq(alice, client_of, package_of):
    """When deleting package sequencing data, only link deleted."""
    fastq = SequencingData.objects.create(
        data_location="anywhere",
        library_name="whatever",
    )
    fastq_hash = fastq.hashes.create(
        algorithm="MD5",
        value="1234ff",
    )
    package_fastq = package_of(alice).assoc_sequencing_datas.create(
        sequencing_data=fastq,
        sequencing_data_hash=fastq_hash,
        filename="file.fastq.gz",
    )
    package_fastq_pk = package_fastq.pk

    endpoint = reverse(
        "v1:submission:packagesequencingdata-detail",
        (package_of(alice).pk, package_fastq.pk),
    )
    response = client_of(alice).delete(endpoint)
    assert response.status_code == 204

    # package-fastq link removed
    assert (
        not package_of(alice)
        .assoc_sequencing_datas.filter(pk=package_fastq_pk)
        .exists()
    )
    # fastq left
    fastq.refresh_from_db()
