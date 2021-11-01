from django.apps import AppConfig


def create_permission_groups(**kwargs):
    from django.contrib.auth.models import Group
    from .constants import GENRE_CATEGORY_CHOICES

    for category in GENRE_CATEGORY_CHOICES:
        Group.objects.get_or_create(name="p-compoadmin-{}".format(str(category[0])))


class CompetitionsConfig(AppConfig):
    name = "competitions"

    def ready(self):
        from django.db.models.signals import post_migrate
        import competitions.signals  # noqa: F401

        post_migrate.connect(create_permission_groups, sender=self)
