import datetime

import pytz
from django.test import TestCase

from .models import Event


class EventTest(TestCase):
    def setUp(self):
        self.event1 = Event.objects.create(
            name="Test Event Å 42",
            location="SüperHœllen",
            start_date=datetime.datetime.utcnow().replace(tzinfo=pytz.utc),
            end_date=datetime.datetime.utcnow().replace(tzinfo=pytz.utc) + datetime.timedelta(days=2),
        )

    def test_string_cast(self):
        self.assertEqual(str(self.event1), self.event1.name)
