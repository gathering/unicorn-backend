from datetime import datetime, timedelta

import pytz
from accounts.models import User
from competitions.constants import *  # noqa: F403
from competitions.models import Competition, Genre
from django.test import TestCase
from matchmaking.constants import *  # noqa: F403
from matchmaking.models import MatchRequest


class MatchRequestModelTestCase(TestCase):
    """
    Test Case for MatchRequest model in Matchmaking app
    """

    def setUp(self):
        # create a user
        self.user1 = User.objects.create_user(
            username="tast",
            email="test@testesen.com",
            password="1234",
            first_name="Test",
            last_name="Testesen",
        )

        # create genres
        self.genre1 = Genre.objects.create(category=GENRE_CATEGORY_OTHER, name="Other")

        now = datetime.utcnow().replace(tzinfo=pytz.utc)

        # create competitions
        self.competition1 = Competition.objects.create(
            genre=self.genre1,
            name="Casemod",
            brief_description="Trololol",
            rules="don't cheat. plox",
            register_time_start=now + timedelta(hours=1),
            register_time_end=now + timedelta(hours=2),
            run_time_start=now + timedelta(hours=3),
            run_time_end=now + timedelta(hours=4),
        )

        # create requests
        self.request1 = MatchRequest.objects.create(
            author=self.user1,
            competition=self.competition1,
            rank=MATCH_REQUEST_RANK_ROOKIE,
            looking_for=MATCH_REQUEST_LOOKING_FOR_GROUP,
            role="adc",
            text="best adc evuhr",
        )

    def test_matchrequest_competition_binding(self):
        """
        Match request competition id must match competition id after creating match request
        """
        self.assertEqual(self.request1.competition.id, self.competition1.id)

    def test_matchrequest_author_binding(self):
        """
        Match request author id must match user id after creating match request
        """
        self.assertEqual(self.user1.id, self.request1.author.id)

    def test_matchrequest_model_str_method(self):
        """
        String method of match request should produce a string containing not modifying data from author and competition
        """
        self.assertEqual(
            self.request1.__str__(),
            "{} looking for {} in {}".format(
                self.user1.display_name,
                self.request1.get_looking_for_display(),
                self.competition1.name,
            ),
        )
