import os

# Testing settings.
#
# Most of the settings are hardcoded,
# Only required settings is database connection.

os.environ["SECRET_KEY"] = "DUMMYSECRETKEYVALUEFORTESTINGENVIRONMENT"  # nosec B105
os.environ["ENVIRONMENT"] = "testing"

# disable AWS creds, in order to catch any non-mocked AWS calls.
# Keys are not None to tell botocore not to search for creds in other places
os.environ["AWS_ACCESS_KEY_ID"] = "DUMMY"  # nosec B105
os.environ["AWS_SECRET_ACCESS_KEY"] = "DUMMY"  # nosec B105
# disable S3 file upload backend
os.environ["DEFAULT_FILE_STORAGE"] = "django.core.files.storage.FileSystemStorage"

# pylint: disable=wildcard-import, unused-wildcard-import, wrong-import-position
from .settings import *
