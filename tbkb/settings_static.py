# App static settings definition.
# They're imported into standard "settings" module.

INSTALLED_APPS = [
    # standard django apps
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_pgviews",  # for postgres matview models support
    # tbkb apps
    "tbkb.apps.TbKbAdminConfig",
    "biosql",
    "genphen",
    "identity",
    "overview",
    "submission",
    "api",
    # rest framework goes after our apps
    # in order to rewrite generateschema command
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "django_auth_adfs",  # Azure AD auth
    "service_objects",  # service layer, encapsulates business-logic
    "django_filters",  # package to filter data
    "django_ses",  # for ses stats admin endpoint
    "fsm_admin2",  # for admin actions on FSM fields
    "drf_standardized_errors",  # for DRF unified errors
    "import_export",  # for data import-export ability from admin panel
    # required to be last, to be sure that exceptions from other apps
    # won't affect data integrity
    "django_cleanup.apps.CleanupConfig",
]

AUTHENTICATION_BACKENDS = [
    # Azure AD frontend & admin section handling
    "django_auth_adfs.backend.AdfsAuthCodeBackend",
    # Azure AD admin section handling
    "django_auth_adfs.backend.AdfsAccessTokenBackend",
    # Needed to log in by username in Django admin, regardless of `allauth`
    # "django.contrib.auth.backends.ModelBackend",
]

# django.contrib.sites is used to make URLs that are pointing to frontend domain
SITE_ID = 1


MIDDLEWARE = [
    "tbkb.middleware.healthcheck.healthcheck_middleware",
    "tbkb.middleware.camelcase.CamelCaseMiddleWare",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tbkb.urls"


WSGI_APPLICATION = "tbkb.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# disable l10n and change default datetime format
# to more appropriate one to display in admin section
# DEPRECATION NOTE: USE_L10N will be removed in django 5.0
USE_L10N = False
DATETIME_FORMAT = "d/m/Y G:i:s e"

DRF_STANDARDIZED_ERRORS = {
    "ENABLE_IN_DEBUG_FOR_UNHANDLED_EXCEPTIONS": False,
    "EXCEPTION_FORMATTER_CLASS": "submission.exceptions.CamelCaseExceptionFormatter",
}


# django_pgviews (django-pgviews-redux) option,
# on migration recreate only changed views/matviews
MATERIALIZED_VIEWS_CHECK_SQL_CHANGED = True
