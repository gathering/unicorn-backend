import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.utils.encoding import smart_text
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from .utils import decode_jwt


class JWTAuthentication(BaseAuthentication):
    """
    Token based authentication using the JSON Web Token standard.

    Client should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """

    www_authenticate_realm = "oscar"

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication. Otherwise returns `None`.
        """
        jwt_value = self._get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            payload = decode_jwt(jwt_value)
        except jwt.ExpiredSignatureError:
            msg = "Signature has expired."
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = "Error decoding signature."
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        self._add_session_details(request, payload)

        user = self.authenticate_credentials(payload, jwt_value)
        return user, payload

    def authenticate_credentials(self, payload, jwt_value):
        """
        Returns an active user that matches the payload's user id and email.
        """
        if getattr(settings, "JWT_AUTH_DISABLED", False):
            return get_user_model().get_anonymous()

        User = get_user_model()
        uid = payload.get("uid")
        email = payload.get("email")

        if not uid or not email:
            msg = "Invalid payload."
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(Q(pk=uid), Q(email=email))
        except User.DoesNotExist:
            user = self.create_user_from_oscar(payload, jwt_value)

            if not user:
                msg = "Invalid signature."
                raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = "User account is disabled."
            raise exceptions.AuthenticationFailed(msg)

        if hasattr(user, "role") and user.role == 4:
            msg = "You have no valid ticket for this event"
            raise exceptions.AuthenticationFailed(msg)

        self.fetch_usercards_from_oscar(payload, jwt_value)

        return user

    def fetch_usercards_from_oscar(self, payload, jwt_value):
        if not hasattr(settings, "OSCAR_HOST"):
            return None

        oscar_url = settings.OSCAR_HOST + "accounts/myprofile/?usercards=1"
        r = requests.get(oscar_url, headers={"Authorization": "JWT " + jwt_value})

        if not r.status_code == 200:
            return

        from users.models import UserCard

        cards = r.json().get("usercards")
        if isinstance(cards, list):
            for card in cards:
                UserCard.objects.get_or_create(user_id=payload.get("uid"), value=card)

    def create_user_from_oscar(self, payload, jwt_value):
        if not hasattr(settings, "OSCAR_HOST"):
            return None

        oscar_url = settings.OSCAR_HOST + "accounts/myprofile/"
        r = requests.get(oscar_url, headers={"Authorization": "JWT " + jwt_value})

        if not r.status_code == 200:
            return None

        User = get_user_model()
        data = r.json()

        u = User(
            id=payload.get("uid"),
            uuid=data["uuid"],
            email=data["email"],
            nick=data["display_name"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )

        if data.get("phone_number", None):
            u.phone_number = data["phone_number"]

        if data.get("row", None):
            if isinstance(data["row"], str):
                if data["row"] == "False":
                    u.row = 0
                else:
                    row = [int(s) for s in data["row"].split() if s.isdigit()]
                    if isinstance(row, list):
                        u.row = row[0]
                    else:
                        u.row = row
            elif isinstance(data["row"], int):
                u.row = data["row"]

        if data.get("seat", None):
            if isinstance(data["seat"], str):
                seat = [int(s) for s in data["seat"].split() if s.isdigit()]
                if isinstance(seat, list):
                    u.seat = seat[0]
                else:
                    u.seat = seat
            elif isinstance(data["seat"], int):
                u.seat = data["seat"]

        # if data.get("tg19_participant", None):
        #    if data.get("compo_access", True):
        #        u.role = 2

        if data.get("crew", None):
            u.role = 1
            u.crew = [data["crew"]]

        else:
            u.role = 2

        u.save()
        return u

    def _get_jwt_value(self, request):
        """
        Extract the actual JWT string for the "Authorization" HTTP header,
        or alternatively from cookies if enabled.
        """
        auth = get_authorization_header(request).split()
        auth_header_prefix = getattr(settings, "JWT_AUTH_HEADER_PREFIX", "JWT")

        if not auth:
            if getattr(settings, "JWT_AUTH_COOKIE", None):
                return request.COOKIES.get(settings.JWT_AUTH_COOKIE)
            return None

        if smart_text(auth[0]) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = "Invalid Authorization header. No credentials provided."
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = "Invalid Authorization header. Credentials string should not contain spaces."
            raise exceptions.AuthenticationFailed(msg)

        jwt_value = auth[1]
        if type(jwt_value) is bytes:
            jwt_value = jwt_value.decode("utf-8")
        return jwt_value

    def _add_session_details(self, request, payload):
        """
        Adds to the session payload details so they can be used anytime.
        """
        try:
            items = payload.iteritems()
        except AttributeError:  # python 3.6
            items = payload.items()

        for k, v in items:
            if k not in ("iat", "exp"):
                request.session["jwt_{}".format(k)] = v

    def authenticate_header(self, request):
        """
        Return a string to be used as a value of the `WWW-Authenticate`
        header in a `401 Unauthorized` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        auth_header_prefix = getattr(settings, "JWT_AUTH_HEADER_PREFIX", "JWT")
        return '{0} realm="{1}"'.format(auth_header_prefix, self.www_authenticate_realm)


class AuthenticateAnonymous(BaseAuthentication):
    def authenticate(self, request):
        anon = get_user_model().get_anonymous()

        return (anon, None)


class JWTAuthBackend(JWTAuthentication, ModelBackend):
    def authenticate(self, request, **kwargs):
        return super(JWTAuthBackend, self).authenticate(request)[0]
