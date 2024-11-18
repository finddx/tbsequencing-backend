from django.contrib.admin.apps import AdminConfig


class TbKbAdminConfig(AdminConfig):
    """Custom admin site."""

    default_site = "tbkb.admin.TbKbAdminSite"
