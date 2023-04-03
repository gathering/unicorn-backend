from datetime import datetime

import pytz
from competitions.models import Competition
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Runs through all competitions and updates state based on current time"

    def handle(self, *args, **kwargs):
        self.stdout.write("=== Starting update_competition_states at %s" % datetime.now().replace(tzinfo=pytz.utc))
        for competition in Competition.objects.all():
            new_state = competition.compute_state()

            if new_state == competition.state:
                self.stdout.write(
                    "- State already correct at %s for competition %s" % (competition.state, competition.name)
                )
                continue

            competition.state = new_state
            self.stdout.write("+ New state set to %s for competition %s" % (competition.state, competition.name))
            competition.save()

        self.stdout.write("=== Finished at %s" % datetime.now().replace(tzinfo=pytz.utc), ending="\n\n")
