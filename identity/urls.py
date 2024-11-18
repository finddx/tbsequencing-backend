from django.urls import include, path

# for url namespacing to work
app_name = "identity"  # pylint: disable=invalid-name

urlpatterns = [
    # To be able to log into browsable DRF Web app
    # Frontend does not need this.
    path("browsable-api/", include("rest_framework.urls", namespace="rest_framework")),
]
