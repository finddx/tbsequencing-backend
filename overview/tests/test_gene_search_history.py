from datetime import timedelta

from django.utils import timezone
from rest_framework.reverse import reverse

from overview.models import GeneSearchHistory


def test_gene_search_history(client_of, alice, mocker):
    """Checking gene_search_history api with their counters ordering."""
    now = timezone.now()

    with mocker.patch("django.utils.timezone.now", return_value=now):
        for dbxref, counter in ((7, 1), (8, 2)):
            GeneSearchHistory.objects.create(
                gene_db_crossref_id=dbxref,
                counter=counter,
            )

    endpoint = reverse("v1:overview:gene-search-history-list")

    response = client_of(alice).get(
        endpoint,
    )
    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            "counter": 2,
            "date": now.strftime("%Y-%m-%d %H:%M:%S"),
            "geneDbCrossrefId": 8,
            "geneName": "dnaN",
            "locusTag": "Rv0002",
        },
        {
            "counter": 1,
            "date": now.strftime("%Y-%m-%d %H:%M:%S"),
            "geneDbCrossrefId": 7,
            "geneName": "dnaA",
            "locusTag": "Rv0001",
        },
    ]


def test_gene_search_history_recently_search(client_of, alice, mocker):
    """Checking gene_search_history api, by two detailed objects with updating counters."""
    now = timezone.now()
    yesterday = now - timedelta(days=1)

    for dbxref, counter, date in ((7, 1, now), (8, 2, yesterday)):
        with mocker.patch("django.utils.timezone.now", return_value=date):
            GeneSearchHistory.objects.create(
                gene_db_crossref_id=dbxref,
                counter=counter,
            )

    endpoint = reverse("v1:overview:gene-search-history-recently")
    response = client_of(alice).get(
        endpoint,
    )
    data = response.json()
    assert data == [
        {
            "counter": 1,
            "date": now.strftime("%Y-%m-%d %H:%M:%S"),
            "geneDbCrossrefId": 7,
            "geneName": "dnaA",
            "locusTag": "Rv0001",
        },
        {
            "counter": 2,
            "date": yesterday.strftime("%Y-%m-%d %H:%M:%S"),
            "geneDbCrossrefId": 8,
            "geneName": "dnaN",
            "locusTag": "Rv0002",
        },
    ]
