import requests
from accounts.constants import USER_ROLE_CREW, USER_ROLE_PARTICIPANT
from accounts.models import User
from competitions.constants import ENTRY_STATUS_QUALIFIED
from competitions.models import Entry, Vote
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


def get_social_user(user: User):
    """
    Helper function to get the relevant social details from a User object.
    """
    if user.role == USER_ROLE_CREW:
        social = user.social_auth.filter(provider="keycloak-crew").first()
        social_type = "crew"

    elif user.role == USER_ROLE_PARTICIPANT:
        social = user.social_auth.filter(provider="keycloak-participant").first()
        social_type = "participant"

    else:
        return None

    return (social, social_type)


@receiver(post_save, sender=Vote)
def user_has_voted(instance: Vote, created, **kwargs):
    # do not process if we don't have a webhook destination
    if not settings.ACHIEVEMENTS_WEBHOOK:
        return

    # only run for first vote per entry
    if not created:
        return

    try:
        # find correct social user
        social, social_type = get_social_user(instance.user)

        # build payload
        payload = {
            "type": "user_has_voted",
            "user": social.extra_data["sub"],
            "user_type": social_type,
            "entry": instance.entry.id,
            "competition": instance.entry.competition.id,
        }

        # send event to achievements
        requests.post(settings.ACHIEVEMENTS_WEBHOOK, json=payload)
    except KeyError:
        return


@receiver(post_save, sender=Entry)
def user_got_qualified_entry(instance: Entry, **kwargs):
    # do not process if we don't have a webhook destination
    if not settings.ACHIEVEMENTS_WEBHOOK:
        return

    # ignore everything that's not qualified
    if not instance.status == ENTRY_STATUS_QUALIFIED:
        return

    for user in instance.contributors.all():
        # find correct social user
        social, social_type = get_social_user(user)

        # build payload
        payload = {
            "type": "user_got_qualified_entry",
            "user": social.extra_data["sub"],
            "user_type": social_type,
            "entry": instance.id,
            "competition": instance.competition.id,
        }

        # send event to achievements
        requests.post(settings.ACHIEVEMENTS_WEBHOOK, json=payload)
