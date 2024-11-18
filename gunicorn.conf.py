# pylint: disable=invalid-name

import gunicorn

# mask "Server" header
gunicorn.SERVER = "unknown"

# https://docs.gunicorn.org/en/stable/settings.html
wsgi_app = "tbkb.wsgi"
workers = 4
# threads = 4  # gthread worker type only
timeout = 600
loglevel = "debug"
bind = ["0.0.0.0:8000"]
