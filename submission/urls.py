from django.urls import include, path
from rest_framework_nested import routers

from . import views

# for url namespacing to work
app_name = "submission"  # pylint: disable=invalid-name


router = routers.DefaultRouter()

# top-level package view set
router.register(r"packages", views.packages.PackageViewSet, basename="package")

# nested package router
package_router = routers.NestedDefaultRouter(router, r"packages", lookup="package")

# nested view sets
package_router.register(r"messages", views.PackageMessagesViewSet, basename="message")
package_router.register(r"mic-tests", views.PackageMICTestsViewSet, basename="mictest")
package_router.register(r"pds-tests", views.PackagePDSTestsViewSet, basename="pdstest")
package_router.register(
    r"contributors",
    views.PackageContributorViewSet,
    basename="contributor",
)
package_router.register(
    r"sequencing-data",
    views.PackageSequencingDataViewSet,
    basename="packagesequencingdata",
)
package_router.register(
    r"sample-aliases",
    views.PackageSampleAliasesViewSet,
    basename="samplealias",
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(package_router.urls)),
]
