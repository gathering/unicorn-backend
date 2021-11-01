import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unicorn.settings")

if settings.SERVE_STATIC_FILES:
    application = StaticFilesHandler(get_wsgi_application())
else:
    application = get_wsgi_application()
