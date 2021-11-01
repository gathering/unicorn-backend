from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q, Sum

from ...models import Category, Level

User = get_user_model()


class Command(BaseCommand):
    help = "Runs through and levels up users with enough points"

    def handle(self, *args, **kwargs):
        for category in Category.objects.all():
            # skip categories with no levels set
            if len(category.levels) < 1:
                self.stdout.write(
                    "- skipping category '{}' due to no levels".format(category.name)
                )
                continue

            for level, req in enumerate(category.levels):
                # skip level 0 and levels with no requirement
                if level == 0 or req == 0:
                    self.stdout.write(
                        "--- skipping level {} in category {} due to no requirement".format(
                            level, category.name
                        )
                    )
                    continue

                # fetch users which should get this level
                users = (
                    User.objects.filter(Q(awards__achievement__category=category))
                    .distinct()
                    .annotate(points=Sum("awards__achievement__points"))
                    .filter(points__gte=req)
                    .exclude(userlevels__level=level)
                )

                if users.count() == 0:
                    self.stdout.write(
                        "++ found no users for level {} in category {} /o\\".format(
                            level, category.name
                        )
                    )
                    continue

                self.stdout.write(
                    "++ found {} matching users for level {} in category {} \\o/".format(
                        users.count(), level, category.name
                    )
                )

                # assign levels for all the users
                for user in users:
                    Level.objects.create(category=category, user=user, level=level)
