from django.urls import include, path
from rest_framework import routers

from . import views

# for url namespacing to work
app_name = "genphen"  # pylint: disable=invalid-name

router = routers.DefaultRouter()

router.register(r"countries", views.CountryViewSet)
router.register(r"drugs", views.DrugViewSet, basename="drug")
router.register(
    r"gene-drug-resistance-associations",
    views.GeneDrugResistanceAssociationsViewSet,
    basename="gene-drug-resistance-association",
)


urlpatterns = [
    path("", include(router.urls)),
]
