from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as BaseUser

from identity.models import User


class UserAdmin(BaseUserAdmin):
    """Custom User admin view."""

    list_display = BaseUserAdmin.list_display + ("date_joined",)
    list_filter = BaseUserAdmin.list_filter + (
        "date_joined",
        "groups",
    )
    ordering = ("-date_joined",)


admin.site.unregister(BaseUser)
admin.site.register(User, UserAdmin)
