from django.contrib.auth import get_user_model
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication


class AuthenticateAnonymous(BaseAuthentication):
    def authenticate(self, request):
        anon = get_user_model().get_anonymous()

        return (anon, None)


class AnonymousScheme(OpenApiAuthenticationExtension):
    target_class = "utilities.authentication.AuthenticateAnonymous"
    name = "anonymous"
    priority = -1

    def get_security_definition(self, auto_schema):
        return {"type": "none"}
