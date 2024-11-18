import re

from djangorestframework_camel_case.util import camelize_re, underscore_to_camel
from drf_standardized_errors.formatter import ExceptionFormatter
from drf_standardized_errors.types import ErrorResponse
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_409_CONFLICT


class Conflict(APIException):
    """API exception for Conflict HTTP status code."""

    status_code = HTTP_409_CONFLICT
    default_code = "conflict"


class CamelCaseExceptionFormatter(ExceptionFormatter):
    """Custom exception formatter."""

    def format_error_response(self, error_response: ErrorResponse):
        """Camelcase error attribute on validation error."""
        if error_response.type == error_response.type.VALIDATION_ERROR:
            for error in error_response.errors:
                if error.attr and "_" in error.attr:
                    error.attr = re.sub(camelize_re, underscore_to_camel, error.attr)

        return super().format_error_response(error_response)
