from datetime import datetime, timedelta

import pytz
from dateutil.parser import parse as dateparser
from django.test import TestCase

from ..constants import (
    COMPETITION_STATE_CLOSED,
    COMPETITION_STATE_FIN,
    COMPETITION_STATE_NEW,
    COMPETITION_STATE_REG_CLOSE,
    COMPETITION_STATE_REG_OPEN,
    COMPETITION_STATE_RUN,
    COMPETITION_STATE_SHOW,
    COMPETITION_STATE_VOTE,
    COMPETITION_STATE_VOTE_CLOSED,
    GENRE_CATEGORY_CREATIVE,
    GENRE_CATEGORY_GAME,
    GENRE_CATEGORY_OTHER,
)
from ..models import Competition, Genre


class CompetitionModelTestCase(TestCase):
    """
    Test Case for models and related behaviour in the competition app
    """

    def setUp(self):
        # create genres
        self.genre1 = Genre.objects.create(category=GENRE_CATEGORY_OTHER, name="Other")
        self.genre2 = Genre.objects.create(
            category=GENRE_CATEGORY_CREATIVE, name="Music"
        )
        self.genre3 = Genre.objects.create(
            category=GENRE_CATEGORY_CREATIVE, name="Programming"
        )
        self.genre4 = Genre.objects.create(category=GENRE_CATEGORY_GAME, name="Game")

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
            team_min=1,
            team_max=5,
        )
        self.competition2 = Competition.objects.create(
            genre=self.genre2,
            name="Themed Music",
            brief_description="Themed Music er en konkurranse hvor du får et tema, og skal"
            "produsere en låt basert på temaet du får tildelt.",
            rules="don't cheat. plox",
            run_time_start=now,
            run_time_end=now + timedelta(hours=2),
        )

    def test_team_required(self):
        """team_required property should be true if we have set values for min and max sizes"""
        self.assertEqual(self.competition1.team_required, True)
        self.assertEqual(self.competition2.team_required, False)

    def test_entries_count_empty(self):
        """competition with no entries should report 0 on entries count"""
        self.assertEqual(self.competition1.entries_count, 0)

    def test_genre_name(self):
        """
        Test to make sure Genre names did not get changed while being inserted into the database
        """
        self.assertEqual(self.genre1.name, "Other")
        self.assertEqual(self.genre2.name, "Music")
        self.assertEqual(self.genre3.name, "Programming")
        self.assertEqual(self.genre4.name, "Game")

    def test_genre_str(self):
        """
        Test to make sure Genre string-casting works as expected
        """
        self.assertEqual(self.genre1.name, str(self.genre1))
        self.assertEqual(self.genre2.name, str(self.genre2))
        self.assertEqual(self.genre3.name, str(self.genre3))
        self.assertEqual(self.genre4.name, str(self.genre4))

    def test_competition_name(self):
        """
        Test to make sure Competition names did not get changed while being inserted into the database
        """
        self.assertEqual(self.competition1.name, "Casemod")
        self.assertEqual(self.competition2.name, "Themed Music")

    def test_competition_str(self):
        """
        Test to make sure Competition string-casting works as expected
        """
        self.assertEqual(self.competition1.name, str(self.competition1))
        self.assertEqual(self.competition2.name, str(self.competition2))

    def test_competition_state(self):
        """
        Test to make sure the state of a Competition is behaving as we expect
        """

        now = dateparser("2020-01-01T09:00:00Z")
        expected = (
            # Timestamps can be either None or ISO8601 timestamp in the following order
            # Register time start/end
            # Run time start/end
            # Vote time start/end
            # Show time start/end
            #
            # Run time in the future
            (
                (
                    None,
                    None,
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T12:00:00Z",
                    None,
                    None,
                    None,
                    None,
                ),
                COMPETITION_STATE_NEW,
                COMPETITION_STATE_RUN,
            ),
            # Registration time in the future
            (
                (
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T12:00:00Z",
                    "2020-01-01T12:00:00Z",
                    "2020-01-01T14:00:00Z",
                    None,
                    None,
                    None,
                    None,
                ),
                COMPETITION_STATE_NEW,
                COMPETITION_STATE_REG_OPEN,
            ),
            # Registration time now, pause before run time
            (
                (
                    "2020-01-01T08:00:00Z",
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T12:00:00Z",
                    "2020-01-01T14:00:00Z",
                    None,
                    None,
                    None,
                    None,
                ),
                COMPETITION_STATE_REG_OPEN,
                COMPETITION_STATE_REG_CLOSE,
            ),
            # Register time now, run time immediately after
            (
                (
                    "2020-01-01T08:00:00Z",
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T12:00:00Z",
                    None,
                    None,
                    None,
                    None,
                ),
                COMPETITION_STATE_REG_OPEN,
                COMPETITION_STATE_RUN,
            ),
            # Between register time end and run time start
            (
                (
                    "2020-01-01T06:00:00Z",
                    "2020-01-01T08:00:00Z",
                    "2020-01-01T12:00:00Z",
                    "2020-01-01T14:00:00Z",
                    None,
                    None,
                    None,
                    None,
                ),
                COMPETITION_STATE_REG_CLOSE,
                COMPETITION_STATE_RUN,
            ),
            # Run time now
            (
                (
                    None,
                    None,
                    "2020-01-01T08:00:00Z",
                    "2020-01-01T10:00:00Z",
                    None,
                    None,
                    None,
                    None,
                ),
                COMPETITION_STATE_RUN,
                COMPETITION_STATE_FIN,
            ),
            # Run time now, something in the future
            (
                (
                    None,
                    None,
                    "2020-01-01T08:00:00Z",
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T12:00:00Z",
                    "2020-01-01T14:00:00Z",
                    None,
                    None,
                ),
                COMPETITION_STATE_RUN,
                COMPETITION_STATE_CLOSED,
            ),
            # Run time now, vote after
            (
                (
                    None,
                    None,
                    "2020-01-01T08:00:00Z",
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T12:00:00Z",
                    None,
                    None,
                ),
                COMPETITION_STATE_RUN,
                COMPETITION_STATE_VOTE,
            ),
            # Run time now, show after
            (
                (
                    None,
                    None,
                    "2020-01-01T08:00:00Z",
                    "2020-01-01T10:00:00Z",
                    None,
                    None,
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T12:00:00Z",
                ),
                COMPETITION_STATE_RUN,
                COMPETITION_STATE_SHOW,
            ),
            # Run time in the past
            (
                (
                    None,
                    None,
                    "2020-01-01T06:00:00Z",
                    "2020-01-01T08:00:00Z",
                    None,
                    None,
                    None,
                    None,
                ),
                COMPETITION_STATE_FIN,
                COMPETITION_STATE_FIN,
            ),
            # Between run time end and vote time start
            (
                (
                    None,
                    None,
                    "2020-01-01T06:00:00Z",
                    "2020-01-01T08:00:00Z",
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T12:00:00Z",
                    None,
                    None,
                ),
                COMPETITION_STATE_CLOSED,
                COMPETITION_STATE_VOTE,
            ),
            # Between run time end and show time start
            (
                (
                    None,
                    None,
                    "2020-01-01T06:00:00Z",
                    "2020-01-01T08:00:00Z",
                    None,
                    None,
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T12:00:00Z",
                ),
                COMPETITION_STATE_CLOSED,
                COMPETITION_STATE_SHOW,
            ),
            # In Vote
            (
                (
                    None,
                    None,
                    "2020-01-01T04:00:00Z",
                    "2020-01-01T06:00:00Z",
                    "2020-01-01T08:00:00Z",
                    "2020-01-01T10:00:00Z",
                    None,
                    None,
                ),
                COMPETITION_STATE_VOTE,
                COMPETITION_STATE_FIN,
            ),
            # In Vote, some pause before show
            (
                (
                    None,
                    None,
                    "2020-01-01T04:00:00Z",
                    "2020-01-01T06:00:00Z",
                    "2020-01-01T08:00:00Z",
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T12:00:00Z",
                    "2020-01-01T14:00:00Z",
                ),
                COMPETITION_STATE_VOTE,
                COMPETITION_STATE_VOTE_CLOSED,
            ),
            # In Vote, next is show
            (
                (
                    None,
                    None,
                    "2020-01-01T04:00:00Z",
                    "2020-01-01T06:00:00Z",
                    "2020-01-01T08:00:00Z",
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T12:00:00Z",
                ),
                COMPETITION_STATE_VOTE,
                COMPETITION_STATE_SHOW,
            ),
            # Vote done, show in the future
            (
                (
                    None,
                    None,
                    "2020-01-01T04:00:00Z",
                    "2020-01-01T05:00:00Z",
                    "2020-01-01T06:00:00Z",
                    "2020-01-01T07:00:00Z",
                    "2020-01-01T10:00:00Z",
                    "2020-01-01T12:00:00Z",
                ),
                COMPETITION_STATE_VOTE_CLOSED,
                COMPETITION_STATE_SHOW,
            ),
            # Showtime
            (
                (
                    None,
                    None,
                    "2020-01-01T04:00:00Z",
                    "2020-01-01T05:00:00Z",
                    "2020-01-01T06:00:00Z",
                    "2020-01-01T07:00:00Z",
                    "2020-01-01T08:00:00Z",
                    "2020-01-01T10:00:00Z",
                ),
                COMPETITION_STATE_SHOW,
                COMPETITION_STATE_FIN,
            ),
        )

        # loop and test the different scenarios
        for times, state, next_state in expected:
            # parse strings into objects
            parsed = list(times)
            for idx, dat in enumerate(times):
                if dat:
                    parsed[idx] = dateparser(dat)

            # set competition fields to parsed timestamps
            self.competition1.register_time_start = parsed[0]
            self.competition1.register_time_end = parsed[1]
            self.competition1.run_time_start = parsed[2]
            self.competition1.run_time_end = parsed[3]
            self.competition1.vote_time_start = parsed[4]
            self.competition1.vote_time_end = parsed[5]
            self.competition1.show_time_start = parsed[6]
            self.competition1.show_time_end = parsed[7]

            # make sure the state machine returns what we expect
            self.assertEqual(self.competition1.compute_state(time=now), state)
            self.assertEqual(
                self.competition1.compute_next_state(state=state), next_state
            )

    def test_next_state(self):
        """Competition next_state property should return correct next state"""
        self.assertEqual(
            self.competition1.next_state,
            self.competition1.compute_next_state(state=self.competition1.state),
        )

    def test_toornament_push_without_id(self):
        """
        Make sure we stop any attemts to push data to the Toornament
        API unless we have set the Tournament ID on the Competition.
        """
        with self.assertRaises(ValueError):
            self.competition1.push_to_toornament()
