from django.apps import AppConfig


def create_default_groups(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission

    from .models import User

    # group for anonymous permissions
    anon = Group.objects.get_or_create(name="p-anonymous")
    anon[0].permissions.add(
        Permission.objects.get(codename="view_genre"),
    )
    anonuser = User.get_anonymous()
    anonuser.groups.add(anon[0])

    # group for default participant access
    human = Group.objects.get_or_create(name="p-participant")
    human[0].permissions.add(
        Permission.objects.get(codename="add_entry"),
        Permission.objects.get(codename="add_vote"),
        Permission.objects.get(codename="add_file"),
        Permission.objects.get(codename="change_file"),
        Permission.objects.get(codename="add_contributor"),
    )

    # group for default crew access
    Group.objects.get_or_create(name="p-crew")


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self):
        import accounts.signals  # noqa: F401
        from django.db.models.signals import post_migrate

        post_migrate.connect(create_default_groups, sender=self)
