from django.contrib.auth.models import Group
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
from social_django.models import UserSocialAuth

from .constants import USER_ROLE_ANON, USER_ROLE_CREW, USER_ROLE_PARTICIPANT
from .models import AutoCrew, User


@receiver(post_save, sender=User)
def give_user_self_permissions(sender, instance, created, **kwargs):
    if created and instance.role is not USER_ROLE_ANON:
        # allow the user to view and change itself
        assign_perm("view_user", instance, instance)
        assign_perm("change_user", instance, instance)


@receiver(post_save, sender=User)
def assign_crew_permission_groups(sender, instance, created, **kwargs):
    if created and instance.role is USER_ROLE_CREW and instance.crew is not None:
        # add group for common crew permissions
        instance.groups.add(Group.objects.get(name="p-crew"))

        # find groups for each of the crews the user is a member of and add them to them
        for c in instance.crew:
            ac = AutoCrew.objects.filter(crew=c).prefetch_related()
            for mapping in ac:
                instance.groups.add(mapping.group)


@receiver(post_save, sender=User)
def add_default_permissions(sender, instance, created, **kwargs):
    if (
        instance.role in [USER_ROLE_CREW, USER_ROLE_PARTICIPANT]
        and not instance.groups.filter(name="p-participant").exists()
    ):
        # add user to default participants group
        instance.groups.add(Group.objects.get(name="p-participant"))


@receiver(pre_save, sender=UserSocialAuth)
def build_discord_avatar_url(instance, **kwargs):
    if instance.provider != "discord":
        return

    avatar = instance.extra_data.get("avatar")
    if avatar:
        instance.extra_data[
            "avatar"
        ] = f"https://cdn.discordapp.com/avatars/{instance.uid}/{avatar}.png"


@receiver(post_save, sender=UserSocialAuth)
def assign_crew_permissions_keycloak(instance, **kwargs):
    if instance.provider != "keycloak-crew":
        return

    # find groups for each of the crews the user is a member of and add them to them
    for g in instance.extra_data.get("groups", []):
        ac = AutoCrew.objects.filter(crew=g).prefetch_related()
        for mapping in ac:
            instance.user.groups.add(mapping.group)

            # if users are added to the crew-group, also add the role.
            if mapping.group.name == 'p-crew':
                instance.user.role = USER_ROLE_CREW
                instance.user.save()

@receiver(post_save, sender=UserSocialAuth)
def assign_participant_permissions_keycloak(instance, **kwargs):
    if instance.provider != "keycloak-participant":
        return

    # blindy assign participant role    
    instance.user.role = USER_ROLE_PARTICIPANT
    instance.user.save()
