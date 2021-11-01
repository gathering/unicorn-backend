import requests
from django.conf import settings
from users.models import User


def get_geekevents_id(user):
    if isinstance(user, User):
        user = user.id

    r = requests.post(
        settings.OSCAR_HOST + "accounts/geekeventsreverseidmapper/", json={"id": user}
    )

    if not r.status_code == 200:
        return None

    return r.json()["user"]
