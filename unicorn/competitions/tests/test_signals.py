from unittest import mock

from competitions.constants import (
    COMPETITION_VISIBILITY_CREW,
    COMPETITION_VISIBILITY_HIDDEN,
    COMPETITION_VISIBILITY_PUBLIC,
    GENRE_CATEGORY_OTHER,
)
from competitions.models import Competition, Genre
from competitions.signals import add_competition_view_published
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.test import TestCase
from django.utils import timezone


class AddCompetitionViewPublishedTestCase(TestCase):
    def setUp(self):
        post_save.connect(add_competition_view_published, sender=Competition)

        self.anon, _ = Group.objects.get_or_create(name="p-anonymous")
        self.crew, _ = Group.objects.get_or_create(name="p-crew")

        now = timezone.now()
        later = now + timezone.timedelta(days=1)

        self.genre = Genre.objects.create(category=GENRE_CATEGORY_OTHER, name="Genre")
        self.competition = Competition.objects.create(
            genre=self.genre,
            name="Competition",
            published=False,
            run_time_start=now,
            run_time_end=later,
        )

    def tearDown(self):
        post_save.disconnect(add_competition_view_published, sender=Competition)

    @mock.patch("competitions.signals.remove_perm")
    def test_visibility_hidden(self, mock_remove):
        self.competition.visibility = COMPETITION_VISIBILITY_HIDDEN
        self.competition.save()

        mock_remove.assert_any_call("view_competition", self.anon, self.competition)
        mock_remove.assert_any_call("view_competition", self.crew, self.competition)

    @mock.patch("competitions.signals.assign_perm")
    @mock.patch("competitions.signals.remove_perm")
    def test_visibility_crew(self, mock_remove, mock_assign):
        self.competition.visibility = COMPETITION_VISIBILITY_CREW
        self.competition.published = False
        self.competition.save()

        mock_remove.assert_any_call("view_competition", self.anon, self.competition)
        mock_remove.assert_any_call("view_competition", self.crew, self.competition)

        self.competition.published = True
        self.competition.save()

        mock_remove.assert_called_with("view_competition", self.anon, self.competition)
        mock_assign.assert_called_with("view_competition", self.crew, self.competition)

    @mock.patch("competitions.signals.assign_perm")
    @mock.patch("competitions.signals.remove_perm")
    def test_visibility_public(self, mock_remove, mock_assign):
        self.competition.visibility = COMPETITION_VISIBILITY_PUBLIC
        self.competition.published = False
        self.competition.save()

        mock_remove.assert_any_call("view_competition", self.crew, self.competition)
        mock_remove.assert_any_call("view_competition", self.anon, self.competition)

        self.competition.published = True
        self.competition.save()

        mock_remove.assert_called_with("view_competition", self.crew, self.competition)
        mock_assign.assert_called_with("view_competition", self.anon, self.competition)
