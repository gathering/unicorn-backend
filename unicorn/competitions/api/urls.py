from rest_framework import routers

from . import views


class CompetitionsRootView(routers.APIRootView):
    def get_view_name(self):
        return "Competitions"


router = routers.DefaultRouter()
router.APIRootView = CompetitionsRootView

# Genres
router.register(r"genres", views.GenreViewSet)

# Competitions
router.register(r"competitions", views.CompetitionViewSet)
router.register(r"results", views.ResultsViewSet, basename="result")
router.register(r"download-entries", views.DownloadViewSet, basename="download")

# Entries
router.register(r"entries", views.EntryViewSet, basename="entry")
router.register(r"votes", views.VoteViewSet, basename="vote")

# Contributors
router.register(r"contributors", views.ContributorViewSet)

app_name = "competitions-api"
urlpatterns = [
    # Competitions
    # url(r'^$', views.CompetitionCLView.as_view(), name='competition-list'),
    # url(r'^(?P<pk>\d+)/$', views.CompetitionRUDView.as_view(), name='competition-detail'),
    # Entries
    # url(r'^(?P<competition>\d+)/entries/$', views.EntriesCLView.as_view(), name='entry-list'),
    # url(r'^(?P<competition>\d+)/entries/(?P<pk>\d+)/$', views.EntriesRUDView.as_view(), name='entry-detail')
] + router.urls
