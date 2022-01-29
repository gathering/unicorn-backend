from datetime import datetime

import pytz
from competitions.constants import COMPETITION_STATE_VOTE, ENTRY_STATUS_QUALIFIED
from competitions.models import Competition
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from guardian.shortcuts import assign_perm, remove_perm


class Command(BaseCommand):
    help = "Runs through all competitions and updates state based on current time"

    def handle(self, *args, **kwargs):
        self.stdout.write(
            "=== Starting update_competition_states at %s" % datetime.now().replace(tzinfo=pytz.utc)
        )
        for competition in Competition.objects.all():
            new_state = competition.compute_state()

            if new_state == competition.state:
                self.stdout.write(
                    "- State already correct at %s for competition %s"
                    % (competition.state, competition.name)
                )
                continue

            competition.state = new_state
            self.stdout.write(
                "+ New state set to %s for competition %s"
                % (competition.state, competition.name)
            )
            competition.save()

            self.set_permissions(competition)

        self.stdout.write(
            "=== Finished at %s" % datetime.now().replace(tzinfo=pytz.utc), ending="\n\n"
        )

    def set_permissions(self, competition):
        if competition.published:
            g = Group.objects.get(name="p-participant")
            entries = competition.entries.filter(status=ENTRY_STATUS_QUALIFIED)
            if entries.exists():
                if competition.state == COMPETITION_STATE_VOTE:
                    for entry in entries:
                        assign_perm("view_entry", g, entry)
                    self.stdout.write("++ Added permissions")
                else:
                    for entry in entries:
                        remove_perm("view_entry", g, entry)
                    self.stdout.write("-- Removed permissions")
