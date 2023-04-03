import os

#########################
#                       #
#   Required settings   #
#                       #
#########################

# This is a list of valid fully-qualified domain names (FQDNs) for the Unicorn server. Unicorn will not permit write
# access to the server via any other hostnames. The first FQDN in the list will be treated as the preferred name.
#
# Example: ALLOWED_HOSTS = ['unicorn.example.com', 'unicorn.internal.local']
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "http://*,https://*").split(",")

# PostgreSQL database configuration.
DATABASE = {
    "NAME": os.getenv("DATABASE_NAME", "unicorn"),  # Database name
    "USER": os.getenv("DATABASE_USER", ""),  # PostgreSQL username
    "PASSWORD": os.getenv("DATABASE_PASSWORD", ""),  # PostgreSQL password
    "HOST": os.getenv("DATABASE_HOST", "localhost"),  # Database server
    "PORT": os.getenv("DATABASE_PORT", ""),  # Database port (leave blank for default)
}

# This key is used for secure generation of random numbers and strings. It must never be exposed outside of this file.
# For optimal security, SECRET_KEY should be at least 50 characters in length and contain a mix of letters, numbers, and
# symbols. Unicorn will not run without this defined. For more information, see
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = os.getenv("SECRET_KEY", "")


#########################
#                       #
#   Optional settings   #
#                       #
#########################

# Specify one or more name and email address tuples representing Unicorn administrators. These people will be notified
# of application errors (assuming correct email settings are provided).
ADMINS = [
    # ['John Doe', 'jdoe@example.com'],
]

# Base URL path if accessing Unicorn within a directory. For example, if installed at http://example.com/unicorn/, set:
# BASE_PATH = 'unicorn/'
BASE_PATH = ""

# API Cross-Origin Resource Sharing (CORS) settings. If CORS_ORIGIN_ALLOW_ALL is set to True, all origins will be
# allowed. Otherwise, define a list of allowed origins using either CORS_ORIGIN_WHITELIST or
# CORS_ORIGIN_REGEX_WHITELIST. For more information, see https://github.com/ottoyiu/django-cors-headers
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = [
    # 'hostname.example.com',
]
CORS_ORIGIN_REGEX_WHITELIST = [
    # r'^(https?://)?(\w+\.)?example\.com$',
]

# Set to True to enable server debugging. WARNING: Debugging introduces a substantial performance penalty and may reveal
# sensitive information about your installation. Only enable debugging while performing testing. Never enable debugging
# on a production system.
DEBUG = os.getenv("DEBUG", False)  # blank becomes false, anything truethy becomes true

# Email settings
EMAIL = {
    "SERVER": "localhost",
    "PORT": 25,
    "USERNAME": "",
    "PASSWORD": "",
    "TIMEOUT": 10,  # seconds
    "FROM_EMAIL": "",
}

# Enable custom logging. Please see the Django documentation for detailed guidance on configuring custom logs:
#   https://docs.djangoproject.com/en/1.11/topics/logging/
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

# Enable custom caching
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_CONNECTION"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "unicorn",
    }
}

# An API consumer can request an arbitrary number of objects =by appending the "limit" parameter to the URL (e.g.
# "?limit=1000"). This setting defines the maximum limit. Setting it to 0 or None will allow an API consumer to request
# all objects by specifying "?limit=0".
MAX_PAGE_SIZE = 1000

# The file path where uploaded media such as image attachments are stored. A trailing slash is not needed. Note that
# the default value of this setting is derived from the installed location.
# MEDIA_ROOT = '/opt/unicorn/unicorn/media'

# Determine how many objects to display per page within a list. (Default: 50)
PAGINATE_COUNT = 50

# Time zone (default: UTC)
TIME_ZONE = "UTC"

# Date/time formatting. See the following link for supported formats:
# https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
DATE_FORMAT = "N j, Y"
SHORT_DATE_FORMAT = "Y-m-d"
TIME_FORMAT = "g:i a"
SHORT_TIME_FORMAT = "H:i:s"
DATETIME_FORMAT = "N j, Y g:i a"
SHORT_DATETIME_FORMAT = "Y-m-d H:i"

# Amazon S3 parameters used by file uploading in entries
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_STORAGE_BUCKET_NAME = ""
AWS_S3_OBJECT_PARAMETERS = {}
