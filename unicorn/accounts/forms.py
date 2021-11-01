from datetime import timedelta

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.forms import Form
from django.utils.translation import gettext_lazy as _
from utilities.forms import BootstrapMixin

remember_time = timedelta(seconds=settings.SESSION_COOKIE_AGE)
consent_duration = timedelta(seconds=settings.CONSENT_DURATION)


class LoginForm(AuthenticationForm, BootstrapMixin):
    remember = forms.BooleanField(
        label="Remember me", required=False, help_text=_(f"{remember_time.days} days")
    )
    challenge = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.pop("autofocus")
        self.fields["username"].widget.attrs.update(
            {
                "placeholder": "Username or Email",
                "class": "appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 "
                "placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:shadow-outline-blue "
                "focus:border-blue-300 focus:z-10 laptop:text-sm laptop:leading-5",
            }
        )

        self.fields["password"].widget.attrs.update(
            {
                "placeholder": "Password",
                "class": "appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 "
                "placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:shadow-outline-blue "
                "focus:border-blue-300 focus:z-10 laptop:text-sm laptop:leading-5",
            }
        )

        self.fields["remember"].widget.attrs.update(
            {
                "class": "form-checkbox h-4 w-4 text-indigo-600 transition duration-150 ease-in-out"
            }
        )


SCOPES_HELP = {
    "openid": "Access your user ID",
    "offline": "Keep you logged in",
    "profile": "Your profile information",
    "email": "Your Email address",
}
SCOPES_HIDDEN = ["openid"]


class ConsentForm(Form):
    remember = forms.BooleanField(
        label="Remember choice",
        required=False,
        initial=True,
        help_text=_(f"{consent_duration.days} days"),
    )
    challenge = forms.CharField(widget=forms.HiddenInput(), required=False)

    accept = bool()

    def __init__(self, *args, **kwargs):
        scopes = kwargs.pop("scopes", [])
        super(ConsentForm, self).__init__(*args, **kwargs)

        for scope in scopes:
            if scope in SCOPES_HIDDEN:
                self.fields[f"scope_{scope}"] = forms.BooleanField(
                    label=scope,
                    required=False,
                    initial=True,
                    help_text=SCOPES_HELP.get(scope, ""),
                    widget=forms.HiddenInput(),
                )

            else:
                self.fields[f"scope_{scope}"] = forms.BooleanField(
                    label=scope,
                    required=False,
                    initial=True,
                    help_text=SCOPES_HELP.get(scope, ""),
                )

    def get_scopes(self):
        scopes = []
        for name, value in self.data.items():
            if name.startswith("scope_") and value == "on":
                scopes.append(name.split("_")[-1])

        return scopes

    def clean(self):
        if "accept" in self.data:
            self.accept = True
        elif "reject" in self.data:
            self.accept = False

        return self.cleaned_data
