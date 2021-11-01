from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class ManagementCommandsTestCase(TestCase):
    """
    Test Case for custom Management Commands. Each test should be named "test_commandname"
    """

    def test_entry_status_progress(self):
        out = StringIO()
        call_command("entry_status_progress", stdout=out)
        self.assertIn("=== Finished at", out.getvalue())

    def test_update_competition_states(self):
        out = StringIO()
        call_command("update_competition_states", stdout=out)
        self.assertIn("=== Finished at", out.getvalue())
