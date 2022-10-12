from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication


class AuthenticateAnonymous(BaseAuthentication):
    def authenticate(self, request):
        anon = get_user_model().get_anonymous()

        return (anon, None)
