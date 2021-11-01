from achievements.constants import *  # noqa: F403
from achievements.models import Achievement, Category
from django.test import TestCase


class AchievementModelTestCase(TestCase):
    """
    Test Case for models and related behaviour in the achievements app
    """

    def setUp(self):
        # create some categories
        self.category1 = Category.objects.create(
            name="Creative", levels=[0, 100, 200, 300, 400]
        )
        self.category2 = Category.objects.create(
            name="Activities", levels=[0, 200, 400, 600, 800]
        )
        self.category3 = Category.objects.create(name="Staying Alive")

        # create a couple of achievements
        self.achievement1 = Achievement.objects.create(
            category=self.category1,
            name="Achievement 1",
            requirement="Do something funny",
            points=10,
            multiple=False,
            hidden=False,
            type=[ACHIEVEMENT_TYPE_CREW, ACHIEVEMENT_TYPE_PARTICIPANT],
        )

    def test_str(self):
        self.assertEqual(str(self.achievement1), self.achievement1.name)

    def test_category_defaults(self):
        # categories with no defined levels should have an empty array
        self.assertEqual(self.category3.levels, [])

        # make sure string casting is correct
        self.assertEqual(str(self.category1), self.category1.name)

    def test_achievement_manual_status(self):
        self.assertTrue(self.achievement1.manual_validation)
