import requests

from .exceptions import AuthRejected

WB_BASE_URL = "https://wannabe.gathering.org"
USER_FIELDS = ["username", "email"]


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {"is_new": False}

    if backend.name not in ["geekevents", "keycloak-crew", "keycloak-participant"]:
        raise AuthRejected(backend.name)

    fields = dict((name, kwargs.get(name, details.get(name))) for name in backend.setting("USER_FIELDS", USER_FIELDS))
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
