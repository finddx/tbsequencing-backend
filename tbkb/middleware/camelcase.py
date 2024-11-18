from djangorestframework_camel_case.settings import api_settings
from djangorestframework_camel_case.util import underscoreize


class CamelCaseMiddleWare:
    """Middleware for receiving query params as camel case."""

    def __init__(self, get_response):
        """Initialize response."""
        self.get_response = get_response

    def __call__(self, request):
        """Receiving response."""
        request.GET = underscoreize(request.GET, **api_settings.JSON_UNDERSCOREIZE)

        response = self.get_response(request)
        return response
