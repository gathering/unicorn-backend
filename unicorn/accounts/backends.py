from django.urls import reverse
from social_core.backends.base import BaseAuth
from social_core.backends.keycloak import KeycloakOAuth2

from .constants import USER_ROLE_MORTAL, USER_ROLE_PARTICIPANT
from .exceptions import AuthRejectedNoTicket

GE_SSO_BASE_URL = "https://www.geekevents.org/sso"

GE_GENDER_MAP = {1: "male", 2: "female"}


class KeycloakCrewOAuth2(KeycloakOAuth2):
    name = "keycloak-crew"

    EXTRA_DATA = [("sub", "sub")]


class KeycloakParticipantOAuth2(KeycloakOAuth2):
    name = "keycloak-participant"

    EXTRA_DATA = [("sub", "sub")]


class GeekEventsSSOAuth(BaseAuth):
    """GeekEvents SSO API authentication backend"""

    name = "geekevents"
    ID_KEY = "id"
    EXTRA_DATA = [("token", "token"), ("timestamp", "timestamp"), ("username", "nick")]

    def get_user_details(self, response):
        """Return user basic information"""
        credentials = {
            "user_id": response.get(self.ID_KEY),
            "timestamp": response.get("timestamp"),
            "token": response.get("token"),
            "event_id": self.setting("GEEKEVENTS_EVENT_ID"),
        }
        userinfo = self.request(f"{GE_SSO_BASE_URL}/extended-userinfo/", method="POST", data=credentials).json()

        # geekevents gives a bool on the status of the request, this is false if
        # token/timestamp is expired (although this seems to never happen)
        if not userinfo.get("status"):
            return {}

        if self.setting("REQUIRE_TICKET") and not userinfo.get("ticket_valid"):
            raise AuthRejectedNoTicket("geekevents")

        return {
            "username": userinfo.get("username"),
            "email": userinfo.get("email"),
            "first_name": userinfo.get("first_name"),
            "last_name": userinfo.get("last_name"),
            "birth": userinfo.get("birth"),
            "phone_number": userinfo.get("phone"),
            "gender": GE_GENDER_MAP.get(userinfo.get("gender"), "other"),
            "role": USER_ROLE_PARTICIPANT if userinfo.get("ticket_valid") else USER_ROLE_MORTAL,
            "row": userinfo.get("ticket_row") or None,
            "seat": userinfo.get("ticket_seat") or None,
        }

    def auth_url(self):
        """Build and return complete URL."""
        redirect_to = self.strategy.absolute_uri(reverse("social:complete", kwargs={"backend": "geekevents"}))

        return f"{GE_SSO_BASE_URL}/?next={redirect_to}"

    def auth_html(self):
        return self.strategy.render_html(tpl=self.setting("FORM_HTML"))

    def auth_complete(self, *args, **kwargs):
        """Completes login process and returns user instance."""
        kwargs.update({"response": self.data, "backend": self})

        return self.strategy.authenticate(*args, **kwargs)
