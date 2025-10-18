import os
import socket
import sys
from pathlib import Path

import environ
from corsheaders.defaults import default_headers
from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured

VERSION = "7.0.0"
REST_FRAMEWORK_VERSION = "7.0"

# Check if we are running tests
TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

# Initialize environment variables
env_file_name = ".env"
if TESTING:
    env_file_name = ".env.testing"

env = environ.Env()
environ.Env.read_env(os.path.join(ROOT_DIR, env_file_name))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="")
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY must be set in environment variables")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", cast=bool, default=False)
INTERNAL_IPS = ("127.0.0.1", "::1", "172.20.0.1")


BASE_PATH = env("BASE_PATH", default="")
if BASE_PATH:
    BASE_PATH = BASE_PATH.strip("/") + "/"  # Enforce trailing slash only

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["http://*", "https://*"])

CORS_ORIGIN_ALLOW_ALL = env.bool("CORS_ORIGIN_ALLOW_ALL", default=True)
CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST", default=[])
CORS_ORIGIN_REGEX_WHITELIST = env.list("CORS_ORIGIN_REGEX_WHITELIST", default=[])
CORS_ALLOW_HEADERS = default_headers + (
    "tus-resumable",
    "upload-length",
    "upload-metadata",
    "upload-offset",
    "X-Unicorn-Entry-Id",
    "X-Unicorn-File-Type",
)


# Logging configuration
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
        "level": env("LOG_LEVEL", default="WARNING"),
    },
}


MEDIA_ROOT = env("MEDIA_ROOT", default=os.path.join(BASE_DIR, "media")).rstrip("/")

MAX_PAGE_SIZE = env.int("MAX_PAGE_SIZE", default=1000)
PAGINATE_COUNT = env.int("PAGINATE_COUNT", default=50)

DATE_FORMAT = env("DATE_FORMAT", default="N j, Y")
DATETIME_FORMAT = env("DATETIME_FORMAT", default="N j, Y g:i a")
SHORT_DATE_FORMAT = env("SHORT_DATE_FORMAT", default="Y-m-d")
SHORT_DATETIME_FORMAT = env("SHORT_DATETIME_FORMAT", default="Y-m-d H:i")
SHORT_TIME_FORMAT = env("SHORT_TIME_FORMAT", default="H:i:s")

TIME_FORMAT = env("TIME_FORMAT", default="g:i a")
TIME_ZONE = env("TIME_ZONE", default="UTC")


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DATABASE_NAME", default="unicorn"),
        "USER": env("DATABASE_USER", default=""),
        "PASSWORD": env("DATABASE_PASSWORD", default=""),
        "HOST": env("DATABASE_HOST", default="localhost"),
        "PORT": env("DATABASE_PORT", default=""),
    }
}


# Cache
# https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-CACHES

REDIS_CONNECTION = env("REDIS_CONNECTION", default=None)
if REDIS_CONNECTION:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_CONNECTION,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
            "KEY_PREFIX": "unicorn",
        }
    }
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


# Authentication

LOGIN_REQUIRED = False
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "oauth2_provider.backends.OAuth2Backend",
    "guardian.backends.ObjectPermissionBackend",
)
AUTH_USER_MODEL = "accounts.User"

ANONYMOUS_USER_NAME = "Anonymous"
GUARDIAN_GET_INIT_ANONYMOUS_USER = "utilities.permissions.get_anonymous_user_instance"
GUARDIAN_MONKEY_PATCH_USER = False

SOCIAL_AUTH_JSONFIELD_ENABLED = True

SESSION_COOKIE_AGE = env("SESSION_COOKIE_AGE", default=60 * 60 * 24 * 30)
CONSENT_DURATION = env("CONSENT_DURATION", default=60 * 60 * 24 * 90)


DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

ACHIEVEMENTS_WEBHOOK = env("ACHIEVEMENTS_WEBHOOK", default=None)

# Email

EMAIL_HOST = env("EMAIL_SERVER", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_HOST_USER = env("EMAIL_USERNAME", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_PASSWORD", default="")
EMAIL_TIMEOUT = env.int("EMAIL_TIMEOUT", default=10)
SERVER_EMAIL = env("EMAIL_FROM_EMAIL", default="")
EMAIL_SUBJECT_PREFIX = "[Unicorn] "

# Installed application
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "corsheaders",
    "debug_toolbar",
    "django_filters",
    "rest_framework",
    "drf_spectacular",
    "guardian",
    "competitions",
    "matchmaking",
    "messaging",
    "utilities",
    "accounts",
    "oauth2_provider",
    "zoodo_utils.tus",
    "social_django",
    "tailwind",
    "theme",
    "core",
    "auditlog",
]

# Middleware
MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "oauth2_provider.middleware.OAuth2TokenMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # 'utilities.middleware.ExceptionHandlingMiddleware',
    "utilities.middleware.LoginRequiredMiddleware",
    "utilities.middleware.APIVersionMiddleware",
    "accounts.middleware.CustomSocialAuthExceptionMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
]

ROOT_URLCONF = "unicorn.urls"

TAILWIND_APP_NAME = "theme"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ]
        },
    }
]

SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ["next", "login_challenge"]
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "accounts.pipeline.annotate_steam",
    "accounts.pipeline.fetch_wannabe_profile",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "accounts.pipeline.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)

# Keycloak crew authentication backend
SOCIAL_AUTH_KEYCLOAK_CREW_KEY = env("SOCIAL_AUTH_KEYCLOAK_CREW_KEY", default="")
SOCIAL_AUTH_KEYCLOAK_CREW_SECRET = env("SOCIAL_AUTH_KEYCLOAK_CREW_SECRET", default="")
SOCIAL_AUTH_KEYCLOAK_CREW_PUBLIC_KEY = env("SOCIAL_AUTH_KEYCLOAK_CREW_PUBLIC_KEY", default="")
SOCIAL_AUTH_KEYCLOAK_CREW_AUTHORIZATION_URL = env("SOCIAL_AUTH_KEYCLOAK_CREW_AUTHORIZATION_URL", default="")
SOCIAL_AUTH_KEYCLOAK_CREW_ACCESS_TOKEN_URL = env("SOCIAL_AUTH_KEYCLOAK_CREW_ACCESS_TOKEN_URL", default="")
SOCIAL_AUTH_KEYCLOAK_CREW_ID_KEY = "email"
SOCIAL_AUTH_KEYCLOAK_CREW_EXTRA_DATA = ["groups"]
SOCIAL_AUTH_KEYCLOAK_CREW_ENABLED = (
    SOCIAL_AUTH_KEYCLOAK_CREW_KEY
    and SOCIAL_AUTH_KEYCLOAK_CREW_SECRET
    and SOCIAL_AUTH_KEYCLOAK_CREW_PUBLIC_KEY
    and SOCIAL_AUTH_KEYCLOAK_CREW_AUTHORIZATION_URL
    and SOCIAL_AUTH_KEYCLOAK_CREW_ACCESS_TOKEN_URL
)
if SOCIAL_AUTH_KEYCLOAK_CREW_ENABLED:
    AUTHENTICATION_BACKENDS = ("accounts.backends.KeycloakCrewOAuth2",) + AUTHENTICATION_BACKENDS

# Keycloak participant authentication backend
SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_KEY = env("SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_KEY", default="")
SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_SECRET = env("SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_SECRET", default="")
SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_PUBLIC_KEY = env("SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_PUBLIC_KEY", default="")
SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_AUTHORIZATION_URL = env(
    "SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_AUTHORIZATION_URL", default=""
)
SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_ACCESS_TOKEN_URL = env("SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_ACCESS_TOKEN_URL", default="")
SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_ID_KEY = "email"
SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_EXTRA_DATA = []
SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_ENABLED = (
    SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_KEY
    and SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_SECRET
    and SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_PUBLIC_KEY
    and SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_AUTHORIZATION_URL
    and SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_ACCESS_TOKEN_URL
)
if SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_ENABLED:
    AUTHENTICATION_BACKENDS = ("accounts.backends.KeycloakParticipantOAuth2",) + AUTHENTICATION_BACKENDS


# Wannabe authentication backend
SOCIAL_AUTH_WANNABE_APP_KEY = env("SOCIAL_AUTH_WANNABE_APP_KEY", default="")
SOCIAL_AUTH_WANNABE_EVENT_NAME = env("SOCIAL_AUTH_WANNABE_EVENT_NAME", default="")
if SOCIAL_AUTH_WANNABE_APP_KEY and SOCIAL_AUTH_WANNABE_EVENT_NAME:
    AUTHENTICATION_BACKENDS = ("accounts.backends.WannabeAPIAuth",) + AUTHENTICATION_BACKENDS

# GeekEvents authentication backend
SOCIAL_AUTH_GEEKEVENTS_EVENT_ID = env("SOCIAL_AUTH_GEEKEVENTS_EVENT_ID", default="")
SOCIAL_AUTH_GEEKEVENTS_REQUIRE_TICKET = env("SOCIAL_AUTH_GEEKEVENTS_REQUIRE_TICKET", cast=bool, default=False)
if SOCIAL_AUTH_GEEKEVENTS_EVENT_ID:
    AUTHENTICATION_BACKENDS = ("accounts.backends.GeekEventsSSOAuth",) + AUTHENTICATION_BACKENDS

# Discord authentication backend
SOCIAL_AUTH_DISCORD_KEY = env("SOCIAL_AUTH_DISCORD_KEY", default="")
SOCIAL_AUTH_DISCORD_SECRET = env("SOCIAL_AUTH_DISCORD_SECRET", default="")
SOCIAL_AUTH_DISCORD_SCOPE = ["identify", "email"]
SOCIAL_AUTH_DISCORD_EXTRA_DATA = [
    ("username", "nick"),
    ("discriminator", "nick_id"),
    ("avatar", "avatar"),
]
if SOCIAL_AUTH_DISCORD_KEY and SOCIAL_AUTH_DISCORD_SCOPE:
    AUTHENTICATION_BACKENDS = ("social_core.backends.discord.DiscordOAuth2",) + AUTHENTICATION_BACKENDS

# Steam OpenID backend
SOCIAL_AUTH_STEAM_API_KEY = env("SOCIAL_AUTH_STEAM_API_KEY", default="")
SOCIAL_AUTH_STEAM_EXTRA_DATA = ["player", "nick", "avatar"]
if SOCIAL_AUTH_STEAM_API_KEY:
    AUTHENTICATION_BACKENDS = ("social_core.backends.steam.SteamOpenId",) + AUTHENTICATION_BACKENDS

# WSGI
WSGI_APPLICATION = "unicorn.wsgi.application"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Internationalization
LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/{}static/".format(BASE_PATH)
STATICFILES_DIRS = (os.path.join(BASE_DIR, "project-static"),)
SERVE_STATIC_FILES = os.environ.get("SERVE_STATIC_FILES", True)

# Media
MEDIA_URL = "/{}media/".format(BASE_PATH)

# Disable default limit of 1000 fields per request. Needed for bulk deletion of objects. (Added in Django 1.10.)
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Allow bigger files
DATA_UPLOAD_MAX_MEMORY_SIZE = 1288490189  # 1,2 GB

# Messages
MESSAGE_TAGS = {messages.ERROR: "danger"}

# Authentication URLs
# LOGIN_URL = "/{}login/".format(BASE_PATH)

# Django filters
FILTERS_NULL_CHOICE_LABEL = "None"
FILTERS_NULL_CHOICE_VALUE = "0"  # Must be a string

# Django REST framework (API)
REST_FRAMEWORK = {
    # "ALLOWED_VERSIONS": [REST_FRAMEWORK_VERSION],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        # "rest_framework.authentication.SessionAuthentication",
        "utilities.authentication.AuthenticateAnonymous",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "utilities.permissions.DjangoObjectPermissionsFilter",
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_PAGINATION_CLASS": "unicorn.api.OptionalLimitOffsetPagination",
    "DEFAULT_PERMISSION_CLASSES": ("utilities.permissions.StandardObjectPermissions",),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "unicorn.api.FormlessBrowsableAPIRenderer",
        # "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_METADATA_CLASS": "unicorn.api.ExtendedMetadata",
    # "DEFAULT_VERSION": REST_FRAMEWORK_VERSION,
    # "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.AcceptHeaderVersioning",
    "PAGE_SIZE": PAGINATE_COUNT,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Spectacular settings (api schema generator)
SPECTACULAR_SETTINGS = {
    "TITLE": "Unicorn API",
    "DESCRIPTION": "Unified Net-based Interface for Competition Organization, Rules and News.",
    "VERSION": REST_FRAMEWORK_VERSION,
    "CONTACT": {
        "name": "@unicorn-halp",
        # "url": "https://gathering.slack.com/",
        "url": "slack://channel?id=G72J7R8R0&team=T02BLBLFZ",
    },
    "SCHEMA_PATH_PREFIX": r"/api/",
    "OAUTH2_FLOWS": ["authorizationCode"],
    "OAUTH2_AUTHORIZATION_URL": ALLOWED_HOSTS[0] + "oauth2/authorize/",
    "OAUTH2_TOKEN_URL": ALLOWED_HOSTS[0] + "oauth2/token/",
    "OAUTH2_SCOPES": ["email"],
}

OAUTH2_PROVIDER = {
    "SCOPES": {
        "identity": "Basic identity information",
        "email": "Contact information",
    },
    "ACCESS_TOKEN_EXPIRE_SECONDS": 60 * 60,
    "REFRESH_TOKEN_EXPIRE_SECONDS": 60 * 60 * 24 * 5,
    "PKCE_REQUIRED": False,
}


WANNABE_APP_ID = ""
WANNABE_API_KEY = ""


TUS_UPLOAD_DIR = os.path.join(ROOT_DIR, "upload")


try:
    HOSTNAME = socket.gethostname()
except Exception:
    HOSTNAME = "localhost"
