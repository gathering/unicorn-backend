from competitions.models import Contributor
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from guardian.shortcuts import assign_perm


class Command(BaseCommand):
    help = "Backfills compoadmin group permissions (view/change/delete) on all existing contributors"

    def handle(self, *args, **kwargs):
        contributors = Contributor.objects.select_related("entry__competition__genre").all()
        total = contributors.count()
        assigned = 0
        skipped = 0

        self.stdout.write("Processing %d contributors..." % total)

        for contributor in contributors:
            category = contributor.entry.competition.genre.category
            group_name = "p-compoadmin-{}".format(str(category))

            try:
                group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        "  Group %s does not exist, skipping contributor %d" % (group_name, contributor.pk)
                    )
                )
                skipped += 1
                continue

            assign_perm("view_contributor", group, contributor)
            assign_perm("change_contributor", group, contributor)
            assign_perm("delete_contributor", group, contributor)
            assigned += 1

        self.stdout.write(
            self.style.SUCCESS("Done. Assigned permissions for %d contributors, skipped %d." % (assigned, skipped))
        )
