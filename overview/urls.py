from django.urls import path, include
from rest_framework_nested import routers

from . import views

# for url namespacing to work
app_name = "overview"  # pylint: disable=invalid-name


router = routers.DefaultRouter()

router.register(
    r"global-drugs",
    views.ResistanceStatsByDrugViewSet,
    basename="global-drug",
)
router.register(
    r"global-drugs/map",
    views.ResistanceStatsByCountryViewSet,
    basename="global-drug-map",
)
router.register(
    r"gene-associations",
    views.GeneAssociationViewSet,
    basename="gene-association",
)
router.register(
    r"drug-gene-infos",
    views.GeneDrugStatsViewSet,
    basename="drug-gene-infos",
)
router.register(r"genes", views.GeneViewSet, basename="gene")
router.register(
    r"gene-search-history",
    views.GeneSearchHistoryViewSet,
    basename="gene-search-history",
)

urlpatterns = [
    path("", include(router.urls)),
    # keep legacy endpoint path
    path(
        "global-samples/",
        views.GlobalResistanceStatsView.as_view(),
        name="global-resistance-stats",
    ),
]
