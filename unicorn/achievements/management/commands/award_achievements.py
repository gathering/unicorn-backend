from achievements.constants import ACHIEVEMENT_TYPE_CREW, ACHIEVEMENT_TYPE_PARTICIPANT
from achievements.models import Achievement, Award
from django.core.management.base import BaseCommand
from django.db.models import QuerySet
from users.constants import USER_ROLE_CREW, USER_ROLE_PARTICIPANT


class Command(BaseCommand):
    help = "Runs through and awards achievements to users which should get them"

    def handle(self, *args, **kwargs):
        # fetch all achievements with querysets
        achievements = Achievement.objects.exclude(manual_validation=True).exclude(
            qs_award__exact=""
        )

        # loop through and execute that shit
        for a in achievements:
            data = {}
            exec(a.qs_award, data)

            # make sure we got a QuerySet back
            if not isinstance(data.get("users", None), QuerySet):
                self.stderr.write(
                    "!! Achievement '{}' did not return a `QuerySet` object".format(
                        a.name
                    )
                )
                continue

            # make sure we have actual users to award
            qs = data["users"]
            if qs.count() < 1:
                self.stdout.write(
                    "-- No users found to receive achievement '{}'".format(a.name)
                )
                continue

            # loop through users
            for user in qs:
                # check crew vs participant
                if not (
                    (
                        user.role == USER_ROLE_PARTICIPANT
                        and str(ACHIEVEMENT_TYPE_PARTICIPANT) in a.type
                    )
                    or (
                        user.role == USER_ROLE_CREW
                        and str(ACHIEVEMENT_TYPE_CREW) in a.type
                    )
                ):
                    continue

                # find existing awards for this user and achievement
                if a.multiple:
                    existing = user.awards.filter(achievement=a).count()
                    handouts = user.count - existing

                    if handouts == 1:
                        Award.objects.create(achievement=a, user=user)
                        self.stdout.write(
                            "++ Gave '{}' to '{}' 1 times".format(
                                a.name, user.display_name
                            )
                        )
                    elif handouts > 1:
                        [
                            Award.objects.create(achievement=a, user=user)
                            for i in range(handouts)
                        ]
                        self.stdout.write(
                            "++ Gave '{}' to '{}' {} times".format(
                                a.name, user.display_name, handouts
                            )
                        )

                else:
                    existing = user.awards.filter(achievement=a).exists()
                    if not existing:
                        Award.objects.create(achievement=a, user=user)
                        self.stdout.write(
                            "++ Gave '{}' to '{}'".format(a.name, user.display_name)
                        )
