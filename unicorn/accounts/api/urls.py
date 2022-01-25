from django.urls import include, path
from rest_framework import routers

from . import views


class UsersRootView(routers.APIRootView):
    """
    Users API root view
    """

    def get_view_name(self):
        return "Users"


router = routers.DefaultRouter()
router.APIRootView = UsersRootView

# Field choices
router.register(r"_choices", views.UserFieldChoicesViewSet, basename="field-choice")

router.register(r"users", views.UserViewSet)

app_name = "accounts-api"
urlpatterns = [
    path("search/", views.SearchView.as_view(), name="accounts-api-search"),
    path("mypermissions/", views.MyGlobalPermissionsView.as_view(), name="accouts-mypermissions"),
    path("", include(router.urls))
]
