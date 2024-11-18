from django.http import HttpRequest, HttpResponse


def healthcheck_middleware(get_response):
    """
    Healthcheck middleware, always returning pong response on /ping request.

    Should be placed before SecurityMiddleware, to avoid ALLOWED_HOSTS check.
    This needed for healthcheck request in order to work properly with AWS ELB.
    """

    def middleware(request: HttpRequest):
        """Actual middleware payload."""
        if request.path_info == "/ping":
            return HttpResponse("pong")

        response = get_response(request)

        return response

    return middleware
