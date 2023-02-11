from django.apps import AppConfig


def create_permission_groups(**kwargs):
    from django.contrib.auth.models import Group, Permission

    from .constants import GENRE_CATEGORY_CHOICES

    p = Permission.objects.get(
        content_type__app_label="competitions", codename="add_competition"
    )
    for category in GENRE_CATEGORY_CHOICES:
        g = Group.objects.get_or_create(name="p-compoadmin-{}".format(str(category[0])))
        if g[1]:
            # add permission if the group was created
            g[0].permissions.add(p)


class CompetitionsConfig(AppConfig):
    name = "competitions"

    def ready(self):
        import competitions.signals  # noqa: F401
        import competitions.signals_achievements  # noqa: F401
        from django.db.models.signals import post_migrate

        post_migrate.connect(create_permission_groups, sender=self)
