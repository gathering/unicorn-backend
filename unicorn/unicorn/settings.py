import os
import socket
import sys

import environ
import sentry_sdk
from corsheaders.defaults import default_headers
from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured
from sentry_sdk.integrations.django import DjangoIntegration

try:
    from unicorn import configuration
except ImportError:
    raise ImproperlyConfigured(
        "Configuration file is not preset. Please define unicorn/unicorn/configuration.py per the documentation"
    )

VERSION = "7.0.0"
REST_FRAMEWORK_VERSION = "7.0"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

TESTING = sys.argv[1:2] == ["test"]
if TESTING:
    environ.Env.read_env(os.path.join(BASE_DIR, "development.example.env"))
else:
    environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Import required configuration parameters
ALLOWED_HOSTS = CSRF_TRUSTED_ORIGINS = DATABASE = SECRET_KEY = SENTRY_DSN = None
for setting in [
    "ALLOWED_HOSTS",
    "CSRF_TRUSTED_ORIGINS",
    "DATABASE",
    "SECRET_KEY",
    "SENTRY_DSN",
]:
    try:
        globals()[setting] = getattr(configuration, setting)
    except AttributeError:
        raise ImproperlyConfigured("Mandatory setting {} is missing from configuration.py.".format(setting))

# Import optional configuration parameters
ADMINS = getattr(configuration, "ADMINS", [])
BASE_PATH = getattr(configuration, "BASE_PATH", "")
if BASE_PATH:
    BASE_PATH = BASE_PATH.strip("/") + "/"  # Enforce trailing slash only
CORS_ORIGIN_ALLOW_ALL = getattr(configuration, "CORS_ORIGIN_ALLOW_ALL", False)
CORS_ORIGIN_REGEX_WHITELIST = getattr(configuration, "CORS_ORIGIN_REGEX_WHITELIST", [])
CORS_ORIGIN_WHITELIST = getattr(configuration, "CORS_ORIGIN_WHITELIST", [])
DEBUG = getattr(configuration, "DEBUG", False)
EMAIL = getattr(configuration, "EMAIL", {})
LOGGING = getattr(configuration, "LOGGING", {})
CACHES = getattr(
    configuration,
    "CACHES",
    {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
MAX_PAGE_SIZE = getattr(configuration, "MAX_PAGE_SIZE", 500)
MEDIA_ROOT = getattr(configuration, "MEDIA_ROOT", os.path.join(BASE_DIR, "media")).rstrip("/")
PAGINATE_COUNT = getattr(configuration, "PAGINATE_COUNT", 50)
DATE_FORMAT = getattr(configuration, "DATE_FORMAT", "N j, Y")
DATETIME_FORMAT = getattr(configuration, "DATETIME_FORMAT", "N j, Y g:i a")
SHORT_DATE_FORMAT = getattr(configuration, "SHORT_DATE_FORMAT", "Y-m-d")
SHORT_DATETIME_FORMAT = getattr(configuration, "SHORT_DATETIME_FORMAT", "Y-m-d H:i")
SHORT_TIME_FORMAT = getattr(configuration, "SHORT_TIME_FORMAT", "H:i:s")
TIME_FORMAT = getattr(configuration, "TIME_FORMAT", "g:i a")
TIME_ZONE = getattr(configuration, "TIME_ZONE", "UTC")
AWS_ACCESS_KEY_ID = getattr(configuration, "AWS_ACCESS_ACCESS_KEY", "")
AWS_SECRET_ACCESS_KEY = getattr(configuration, "AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = getattr(configuration, "AWS_STORAGE_BUCKET_NAME", "")
AWS_S3_OBJECT_PARAMETERS = getattr(configuration, "AWS_S3_OBJECT_PARAMETERS", {})

LOGIN_REQUIRED = False

CORS_ALLOW_HEADERS = default_headers + (
    "tus-resumable",
    "upload-length",
    "upload-metadata",
    "upload-offset",
    "X-Unicorn-Entry-Id",
    "X-Unicorn-File-Type",
)

# Database
configuration.DATABASE.update({"ENGINE": "django.db.backends.postgresql"})
DATABASES = {"default": configuration.DATABASE}
# Authentication
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "oauth2_provider.backends.OAuth2Backend",
    "guardian.backends.ObjectPermissionBackend",
)
AUTH_USER_MODEL = "accounts.User"

ANONYMOUS_USER_NAME = "Anonymous"
GUARDIAN_GET_INIT_ANONYMOUS_USER = "utilities.permissions.get_anonymous_user_instance"
GUARDIAN_MONKEY_PATCH = False

SOCIAL_AUTH_JSONFIELD_ENABLED = True

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

SESSION_COOKIE_AGE = env("SESSION_COOKIE_AGE", default=60 * 60 * 24 * 30)
CONSENT_DURATION = env("CONSENT_DURATION", default=60 * 60 * 24 * 90)

ACHIEVEMENTS_WEBHOOK = env("ACHIEVEMENTS_WEBHOOK", default=None)

# Email
EMAIL_HOST = EMAIL.get("SERVER")
EMAIL_PORT = EMAIL.get("PORT", 25)
EMAIL_HOST_USER = EMAIL.get("USERNAME")
EMAIL_HOST_PASSWORD = EMAIL.get("PASSWORD")
EMAIL_TIMEOUT = EMAIL.get("TIMEOUT", 10)
SERVER_EMAIL = EMAIL.get("FROM_EMAIL")
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
]

if SENTRY_DSN is not False:
    INSTALLED_APPS = ["raven.contrib.django.raven_compat"] + INSTALLED_APPS

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
]

ROOT_URLCONF = "unicorn.urls"

TAILWIND_APP_NAME = "theme"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR + "/templates/"],
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
SOCIAL_AUTH_KEYCLOAK_CREW_KEY = env("SOCIAL_AUTH_KEYCLOAK_CREW_KEY")
SOCIAL_AUTH_KEYCLOAK_CREW_SECRET = env("SOCIAL_AUTH_KEYCLOAK_CREW_SECRET")
SOCIAL_AUTH_KEYCLOAK_CREW_PUBLIC_KEY = env("SOCIAL_AUTH_KEYCLOAK_CREW_PUBLIC_KEY")
SOCIAL_AUTH_KEYCLOAK_CREW_AUTHORIZATION_URL = env("SOCIAL_AUTH_KEYCLOAK_CREW_AUTHORIZATION_URL")
SOCIAL_AUTH_KEYCLOAK_CREW_ACCESS_TOKEN_URL = env("SOCIAL_AUTH_KEYCLOAK_CREW_ACCESS_TOKEN_URL")
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
SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_KEY = env("SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_KEY")
SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_SECRET = env("SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_SECRET")
SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_PUBLIC_KEY = env("SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_PUBLIC_KEY")
SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_AUTHORIZATION_URL = env("SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_AUTHORIZATION_URL")
SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_ACCESS_TOKEN_URL = env("SOCIAL_AUTH_KEYCLOAK_PARTICIPANT_ACCESS_TOKEN_URL")
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
SOCIAL_AUTH_WANNABE_APP_KEY = env("SOCIAL_AUTH_WANNABE_APP_KEY")
SOCIAL_AUTH_WANNABE_EVENT_NAME = env("SOCIAL_AUTH_WANNABE_EVENT_NAME")
if SOCIAL_AUTH_WANNABE_APP_KEY and SOCIAL_AUTH_WANNABE_EVENT_NAME:
    AUTHENTICATION_BACKENDS = ("accounts.backends.WannabeAPIAuth",) + AUTHENTICATION_BACKENDS

# GeekEvents authentication backend
SOCIAL_AUTH_GEEKEVENTS_EVENT_ID = env("SOCIAL_AUTH_GEEKEVENTS_EVENT_ID")
if SOCIAL_AUTH_GEEKEVENTS_EVENT_ID:
    AUTHENTICATION_BACKENDS = ("accounts.backends.GeekEventsSSOAuth",) + AUTHENTICATION_BACKENDS

# Discord authentication backend
SOCIAL_AUTH_DISCORD_KEY = env("SOCIAL_AUTH_DISCORD_KEY")
SOCIAL_AUTH_DISCORD_SECRET = env("SOCIAL_AUTH_DISCORD_SECRET")
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
STATIC_ROOT = BASE_DIR + "/static/"
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
        "rest_framework.authentication.SessionAuthentication",
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

# Django debug toolbar
INTERNAL_IPS = ("127.0.0.1", "::1", "172.20.0.1")

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


TUS_UPLOAD_DIR = BASE_DIR + "/upload/"

# Sentry configuration
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()],
    environment="development" if "dev" in VERSION else "production",
    release=VERSION,
    send_default_pii=True,
)


try:
    HOSTNAME = socket.gethostname()
except Exception:
    HOSTNAME = "localhost"
