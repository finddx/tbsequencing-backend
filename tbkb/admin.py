from django.contrib import admin
from django.conf import settings


class TbKbAdminSite(admin.AdminSite):
    """Customized admin site."""

    site_header = settings.SITE_HEADER
