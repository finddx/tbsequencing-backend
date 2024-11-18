from django.urls import path, include


def trigger_error(request):  # pylint: disable=unused-argument
    """Ensure sentry is working properly."""
    return 1 / 0


urlpatterns = [
    path("submission/", include("submission.urls")),
    path("identity/", include("identity.urls")),
    path("genphen/", include("genphen.urls")),
    path("overview/", include("overview.urls")),
    path("sentry-debug/", trigger_error),
]
