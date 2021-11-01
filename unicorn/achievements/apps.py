from django.apps import AppConfig


def create_permission_groups(**kwargs):
    from django.contrib.auth.models import Group, Permission

    # add permissions group
    g = Group.objects.get_or_create(name="p-achievement-admin")
    g[0].permissions.add(
        # add general permissions to categories
        Permission.objects.get(codename="view_category"),
        Permission.objects.get(codename="add_category"),
        Permission.objects.get(codename="change_category"),
        Permission.objects.get(codename="delete_category"),
        # add general permissions to achievements
        Permission.objects.get(codename="view_achievement"),
        Permission.objects.get(codename="add_achievement"),
        Permission.objects.get(codename="change_achievement"),
        Permission.objects.get(codename="delete_achievement"),
    )


class AchievementsConfig(AppConfig):
    name = "achievements"

    def ready(self):
        from django.db.models.signals import post_migrate
        import achievements.signals  # noqa: F401

        post_migrate.connect(create_permission_groups, sender=self)
