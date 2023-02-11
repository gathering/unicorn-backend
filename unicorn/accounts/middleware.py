from django.urls import reverse
from social_core.exceptions import AuthAlreadyAssociated, NotAllowedToDisconnect
from social_django.middleware import SocialAuthExceptionMiddleware


class CustomSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def raise_exception(self, request, exception):
        return False

    def get_redirect_uri(self, request, exception):
        if request.user.is_authenticated:
            return reverse("accounts:profile")

        else:
            backend = getattr(exception, "backend", {})
            if getattr(backend, "name", "") == "wannabe":
                return reverse("accounts:login-provider", kwargs={"provider": "wannabe"})

            return request.session.get("next", None) or reverse("accounts:login")

    def get_message(self, request, exception):
        msg = str(exception)

        if isinstance(exception, NotAllowedToDisconnect):
            msg = "You cannot disconnect your only active authentication method!"

        elif isinstance(exception, AuthAlreadyAssociated):
            msg = "That account is already associated with another user."

        return msg
