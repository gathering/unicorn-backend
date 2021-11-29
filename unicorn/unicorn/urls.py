from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic.base import RedirectView
from django.views.static import serve
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from zoodo_utils.tus.views import TusUpload

from unicorn.views import APIRootView

_patterns = [
    # Redirect random requests to API
    path(
        "",
        RedirectView.as_view(url=reverse_lazy("api-root"), permanent=False),
        name="home",
    ),
    # API
    path("api/", APIRootView.as_view(), name="api-root"),
    path("api/accounts/", include("accounts.api.urls")),
    path("api/achievements/", include("achievements.api.urls")),
    path("api/competitions/", include("competitions.api.urls")),
    path("api/matchmaking/", include("matchmaking.api.urls")),
    # API Docs
    path("api/openapi.yaml", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Serving static media in Django to pipe it through LoginRequiredMiddleware
    path("media/<path>", serve, {"document_root": settings.MEDIA_ROOT}),
    # TUS Uploads
    path("upload/", TusUpload.as_view(), name="tus_upload"),
    re_path(
        r"^upload/(?P<resource_id>[0-9a-z-]+)$",
        TusUpload.as_view(),
        name="tus_upload_chunks",
    ),
    # Favicon
    re_path(
        r"^favicon\.ico$",
        RedirectView.as_view(url="/static/favicon.ico", permanent=True),
    ),
    # Accounts and authentication
    path("accounts/", include("accounts.urls")),
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("social/", include("social_django.urls", namespace="social")),
    # Admin
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar

    _patterns += [path("__debug__/", include(debug_toolbar.urls))]

# Prepend BASE_PATH
urlpatterns = [path("{}".format(settings.BASE_PATH), include(_patterns))]
