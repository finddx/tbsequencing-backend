"""
WSGI config for tbkb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tbkb.settings")

# we will use gevent worker,
# so we need to patch the stuff to work accordingly
from gevent import monkey  # pylint: disable=wrong-import-position

monkey.patch_all()

from psycogreen.gevent import patch_psycopg  # pylint: disable=wrong-import-position

patch_psycopg()

# pylint: disable=wrong-import-position
from django.core.wsgi import (
    get_wsgi_application,
)

application = get_wsgi_application()
