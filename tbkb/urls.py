"""
tbkb URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/

Examples
--------
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    # some backend defs
    path("admin/django-ses/", include("django_ses.urls")),
    path("admin/", admin.site.urls),
    # our API url definitions
    path("api/v1/", include(("api.urls", "api"), namespace="v1")),
    # path("api/v2/", include(("api.urls", "api"), namespace='v2')),
    # DRF browsable API login endpoint
    # path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # Azure AD auth
    path("api/v1/oauth2/", include("django_auth_adfs.urls")),
    # path("api/v1/oauth2drf/", include("django_auth_adfs.drf_urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
