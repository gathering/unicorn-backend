from datetime import datetime

import pytz
from competitions.constants import (
    ENTRY_STATUS_DRAFT,
    ENTRY_STATUS_NEW,
    ENTRY_STATUS_QUALIFIED,
)
from competitions.models import Entry
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Runs through all entries and updates status based on given parameters"

    def handle(self, *args, **kwargs):
        self.stdout.write(
            "=== Starting at %s" % datetime.now().replace(tzinfo=pytz.utc)
        )
        for entry in Entry.objects.all().prefetch_related("competition"):
            is_valid = entry.validate_contributors()

            if (
                is_valid
                and entry.competition.autoqualify
                and entry.status == ENTRY_STATUS_DRAFT
            ):
                self.stdout.write(
                    '+ Entry "%s" in %s was progress from Draft to Qualified'
                    % (entry.title, entry.competition.name)
                )
                entry.status = ENTRY_STATUS_QUALIFIED
                entry.save()
                continue

            if is_valid and entry.status == ENTRY_STATUS_DRAFT:
                self.stdout.write(
                    '+ Entry "%s" in %s was progressed from Draft to New'
                    % (entry.title, entry.competition.name)
                )
                entry.status = ENTRY_STATUS_NEW
                entry.save()
                continue

            self.stdout.write(
                '- Entry "%s" in %s was not updated'
                % (entry.title, entry.competition.name)
            )

        self.stdout.write(
            "=== Finished at %s" % datetime.now().replace(tzinfo=pytz.utc)
        )
