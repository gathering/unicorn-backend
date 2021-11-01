from django.conf.urls import url
from rest_framework import routers

from . import views


class MatchmakingRootView(routers.APIRootView):
    def get_view_name(self):
        return "Matchmaking"


router = routers.DefaultRouter()
router.APIRootView = MatchmakingRootView

# Field choices
router.register(
    r"_choices", views.MatchMakingFieldChoicesViewSet, basename="field-choice"
)

# Matchmaking Requests
router.register(r"requests", views.MatchRequestViewSet)

app_name = "matchmaking-api"
urlpatterns = [
    url(r"^recommended/$", views.RecommendedListView.as_view(), name="recommended-list")
    # Competitions
    # url(r'^$', views.CompetitionCLView.as_view(), name='competition-list'),
    # url(r'^(?P<pk>\d+)/$', views.CompetitionRUDView.as_view(), name='competition-detail'),
    # Entries
    # url(r'^(?P<competition>\d+)/entries/$', views.EntriesCLView.as_view(), name='entry-list'),
    # url(r'^(?P<competition>\d+)/entries/(?P<pk>\d+)/$', views.EntriesRUDView.as_view(), name='entry-detail')
] + router.urls
