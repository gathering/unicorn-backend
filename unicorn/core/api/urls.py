from django.urls import include, path
from rest_framework import routers

from . import views


class CoreRootView(routers.APIRootView):
    """
    Core API root view
    """

    def get_view_name(self):
        return "Core"


router = routers.DefaultRouter()
router.APIRootView = CoreRootView

router.register(r"events", views.EventViewSet)

app_name = "core-api"
urlpatterns = [
    path("", include(router.urls)),
]
