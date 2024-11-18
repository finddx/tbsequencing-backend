from rest_framework.management.commands import generateschema

from rest_framework.schemas.openapi import SchemaGenerator


class ApiV1SchemaGenerator(SchemaGenerator):
    """OpenAPI schema generator, supplemented with app-specific data."""

    def __init__(self, **kwargs):  # pylint: disable=unused-argument
        """Initialize schema generator with API V1 parameters."""
        super().__init__(
            title="TbKb Backend API",
            url=None,
            description="WHO Global Tuberculosis Program backend API",
            patterns=None,
            urlconf="api.urls",
            version="v1",
        )

    @staticmethod
    def describe_servers(schema: dict):
        """Describe available servers."""
        schema["servers"] = [
            {
                "url": "http://localhost:8000/api/v1",
                "description": "Development server",
            },
        ]

    @staticmethod
    def describe_security(schema: dict):
        """Describe security schemes."""
        schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            },
        }
        schema["security"] = [
            {
                "bearerAuth": [],
            },
        ]

    def get_schema(self, *args, **kwargs):
        """Supplement generated schema with additional data."""
        schema = super().get_schema(*args, **kwargs)

        self.describe_servers(schema)
        self.describe_security(schema)

        return schema


class Command(generateschema.Command):
    """OpenAPI schema generator specific for API V1."""

    def get_generator_class(self):
        """Return API V1 schema generator class."""
        return ApiV1SchemaGenerator
