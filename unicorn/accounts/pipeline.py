import requests
from social_core.exceptions import AuthFailed, AuthUnreachableProvider

from .exceptions import AuthRejected

WB_BASE_URL = "https://wannabe.gathering.org"
USER_FIELDS = ["username", "email"]


def authenticate_wannabe(strategy, backend, response, *args, **kwargs):
    if backend.name != "wannabe":
        return

    credentials = {
        "app": backend.setting("WANNABE_APP_KEY"),
        "username": strategy.request_data().get("username"),
        "password": strategy.request_data().get("password"),
    }

    # poll the wannabe auth api
    try:
        r = requests.post(
            f"{WB_BASE_URL}/{backend.setting('WANNABE_EVENT_NAME')}/api/auth/",
            headers={"Accept": "application/json"},
            json=credentials,
        )

    # wannabe is down?
    except requests.ConnectionError as err:
        raise AuthUnreachableProvider(err)

    # nope, sorry
    if not r.status_code == 200:
        res = r.json()
        msg = res.get("error", {}).get("name", "")

        raise AuthFailed(backend, msg)

    return {"response": dict(r.json(), **response)}


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {"is_new": False}

    if backend.name not in ["keycloak", "wannabe", "geekevents"]:
        raise AuthRejected(backend.name)

    fields = dict(
        (name, kwargs.get(name, details.get(name)))
        for name in backend.setting("USER_FIELDS", USER_FIELDS)
    )
    if not fields:
        return

    return {"is_new": True, "user": strategy.create_user(**fields)}


def annotate_steam(backend, details, *args, **kwargs):
    if backend.name != "steam":
        return

    extra = {
        "username": details.get("player").get("personaname"),
        "avatar": details.get("player").get("avatarfull"),
    }

    return {"details": dict(extra, **details)}
