from datetime import date

from django.contrib.auth.models import Group
from django.test import TestCase

from ..constants import USER_DISPLAY_FIRST_LAST, USER_ROLE_PARTICIPANT
from ..models import AutoCrew, User, UserCard


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="test1",
            first_name="Test",
            last_name="Testesen",
            email="test@testesen.lan",
            role=USER_ROLE_PARTICIPANT,
            display_name_format=USER_DISPLAY_FIRST_LAST,
        )

    def test_str(self):
        self.assertEqual(
            str(self.user1), f"{self.user1.display_name} ({self.user1.uuid})"
        )

    def test_id(self):
        self.assertEqual(self.user1.id, self.user1.uuid)

    def test_display_name(self):
        self.assertEqual(self.user1.display_name, "Test Testesen")

    def test_age(self):
        years = 20

        user1 = User.objects.get(username="test1")
        self.assertEqual(user1.age, None)

        user1.birth = str(
            date(
                year=date.today().year - years,
                month=date.today().month,
                day=date.today().day,
            )
        )
        user1.save()
        self.assertEqual(user1.age, None)

        user1.refresh_from_db()
        self.assertEqual(user1.age, years)


class UserCardModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="test1",
            first_name="Test",
            last_name="Testesen",
            email="test@testesen.lan",
            role=USER_ROLE_PARTICIPANT,
            display_name_format=USER_DISPLAY_FIRST_LAST,
        )
        self.uc1 = UserCard.objects.create(user=self.user1, value="042C84BAE14C81")

    def test_str(self):
        self.assertEqual(str(self.uc1), "042C84BAE14C81 for user Test Testesen")


class AutoCrewModelTestCase(TestCase):
    def setUp(self):
        self.group1 = Group.objects.create(name="crew-name-group")
        self.ac1 = AutoCrew.objects.create(crew="Crew:Name", group=self.group1)

    def test_str(self):
        self.assertEqual(str(self.ac1), "Crew:Name to group crew-name-group")
