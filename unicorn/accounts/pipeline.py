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

    if backend.name not in ["keycloak-crew", "keycloak-participant"]:
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


def fetch_wannabe_profile(backend, details, response, *args, **kwargs):
    # ignore for all other backends than crew
    if backend.name != "keycloak-crew":
        return

    # start by authenticating to wannabe with our service credentials
    try:
        auth = requests.post(
            f"{WB_BASE_URL}/api/auth/services/login",
            headers={"Accept": "application/json"},
            json={
                "client_id": backend.setting("KEYCLOAK_CREW_KEY"),
                "client_secret": backend.setting("KEYCLOAK_CREW_SECRET"),
                "scope": "external-wannabe-service-user profile",
            },
        )
    except requests.ConnectionError:
        return

    # extract access token and use it to fetch the users profile
    access_token = auth.json()["access_token"]
    try:
        profile = requests.get(
            f"{WB_BASE_URL}/api/profile/profile/{response.get('sub')}",
            headers={
                "Accept": "application/json",
                "Cookie": f"wannabe_jwt={access_token}",
            },
        )
    except requests.ConnectionError:
        return

    # extract profile fields and save those we want to keep
    data = profile.json()
    extra = {
        "username": data.get("nickname"),
        "phone_number": data.get("phone"),
    }
    details.pop("username")

    return {"details": dict(**extra, **details)}
