from rest_framework import routers

from . import views


class AchievementsRootView(routers.APIRootView):
    """
    Achievements API root view
    """

    def get_view_name(self):
        return "Achievements"


router = routers.DefaultRouter()
router.APIRootView = AchievementsRootView

# Field choices
# router.register(r'_choices', views.AchievementsFieldChoicesViewSet, base_name='field-choice')

# All the important stuff
router.register(r"teams", views.TeamViewSet)
router.register(r"categories", views.CategoryViewSet)
router.register(r"levels", views.LevelViewSet)
router.register(r"achievements", views.AchievementViewSet)
router.register(r"awards", views.AwardViewSet)
router.register(r"stations", views.NfcStationViewSet)
router.register(r"scans", views.NfcScanViewSet)

app_name = "achievements-api"
urlpatterns = router.urls
