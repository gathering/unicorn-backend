from datetime import datetime, timedelta

import pytz
from accounts.constants import *  # noqa: F403
from accounts.models import User
from competitions.constants import *  # noqa: F403
from competitions.models import Competition, Genre
from django.test import TestCase
from matchmaking.constants import *  # noqa: F403
from matchmaking.models import MatchRequest


class MatchRequestViewTest(TestCase):
    def setUp(self):
        # create a user
        self.user1 = User.objects.create_user(
            # we need to specify the UUID to keep it the same everywhere. otherwise
            # we would have to re-fetch from the database to get the correct UUID.
            uuid="72727948-07a0-4d22-a1da-7451e4aa15cc",
            username="test",
            email="test@testesen.com",
            password="1234",
            first_name="Test",
            last_name="Testesen",
            role=USER_ROLE_PARTICIPANT,
            checked_in=True,
        )
        self.user2 = User.objects.create_user(
            uuid="b1df31cd-9f49-4b7a-96d2-5de6ae333cb3",
            username="tust",
            email="tust@testesen.com",
            password="1234",
            first_name="Tust",
            last_name="Tustusun",
            role=USER_ROLE_PARTICIPANT,
            checked_in=True,
        )

        # create genres
        self.gameGenre = Genre.objects.create(category=GENRE_CATEGORY_GAME, name="Game")
        self.creativeGenre = Genre.objects.create(category=GENRE_CATEGORY_CREATIVE, name="Programming")

        now = datetime.utcnow().replace(tzinfo=pytz.utc)

        # create competitions
        self.competition1 = Competition.objects.create(
            genre=self.gameGenre,
            name="CS1.6",
            brief_description="Headshots yo!",
            rules="don't cheat. plox",
            register_time_start=now + timedelta(hours=1),
            register_time_end=now + timedelta(hours=2),
            run_time_start=now + timedelta(hours=3),
            run_time_end=now + timedelta(hours=4),
        )
        self.competition2 = Competition.objects.create(
            genre=self.creativeGenre,
            name="Small HTML",
            brief_description="Compress the HTML",
            rules="don't cheat. plox",
            register_time_start=now + timedelta(hours=1),
            register_time_end=now + timedelta(hours=2),
            run_time_start=now + timedelta(hours=3),
            run_time_end=now + timedelta(hours=4),
        )

        # create requests
        self.mr1 = MatchRequest.objects.create(
            author=self.user1,
            competition=self.competition1,
            rank=MATCH_REQUEST_RANK_ROOKIE,
            looking_for=MATCH_REQUEST_LOOKING_FOR_GROUP,
            role="adc",
            text="mr1 best adc evuhr",
        )
        self.mr2 = MatchRequest.objects.create(
            author=self.user1,
            competition=self.competition2,
            rank=MATCH_REQUEST_RANK_INTERMEDIATE,
            looking_for=MATCH_REQUEST_LOOKING_FOR_PLAYER,
            role="adc",
            text="mr2 best adc evuhr",
            active=False,
        )
        self.mr3 = MatchRequest.objects.create(
            author=self.user2,
            competition=self.competition2,
            rank=MATCH_REQUEST_RANK_EXPERT,
            looking_for=MATCH_REQUEST_LOOKING_FOR_GROUP,
            role="adc",
            text="mr3 best adc evuhr",
            active=False,
        )
        self.mr4 = MatchRequest.objects.create(
            author=self.user2,
            competition=self.competition1,
            rank=MATCH_REQUEST_RANK_INTERMEDIATE,
            looking_for=MATCH_REQUEST_LOOKING_FOR_PLAYER,
            role="adc",
            text="mr4 best adc evuhr",
        )
        self.response = self.client.login(username=self.user1.username, password="1234")

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/api/matchmaking/requests/")
        self.assertEqual(response.status_code, 200)

    def test_only_active_or_own_visible(self):
        """We should only be able to view our own MatchRequests, and those that are active (i.e. publicly visible)"""
        response = self.client.get("/api/matchmaking/requests/")
        self.assertEqual(response.data["count"], 3)

        for mr in response.data["results"]:
            self.assertTrue(mr["author"]["uuid"] == self.user1.uuid or mr["active"] is True)

    def test_recommendations(self):
        response = self.client.get("/api/matchmaking/recommended/")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.mr4.id)
