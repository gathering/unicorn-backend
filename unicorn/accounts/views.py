from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from .forms import LoginForm

# make sure we have the correct User model
User = get_user_model()


class ProfileView(LoginRequiredMixin, View):
    template_name = "accounts/profile.html"

    def get(self, request):
        linked_accounts = request.user.social_auth.all()

        return render(request, self.template_name, {"linked_accounts": linked_accounts})


class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request, **kwargs):
        # we might also have a provider login
        provider = kwargs.get("provider", "")

        if not provider and request.user.is_authenticated:
            redirect_to = request.GET.get("next", "") or reverse("accounts:profile")
            return HttpResponseRedirect(redirect_to)

        form = LoginForm(request)
        return render(
            request, self.template_name, {"form": form, "provider": provider, "next": request.GET.get("next", "")}
        )

    def post(self, request, **kwargs):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            # authenticate user
            auth_login(request, form.get_user())

            # determine where to direct user after successful regular login
            messages.info(request, "Logged in as {}.".format(request.user.display_name))
            redirect_to = request.POST.get("next", "") or reverse("accounts:profile")
            return HttpResponseRedirect(redirect_to)

        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def get(self, request):
        # prepare default redirect url
        redirect_to = request.GET.get("next", "") or reverse("accounts:login")

        # only take real action if we are actually logged in
        if request.user and request.user.is_authenticated:
            auth_logout(request)
            messages.info(request, "You have been logged out.")

        # also make sure to clear any session key cookie, just in case
        response = HttpResponseRedirect(redirect_to)
        response.delete_cookie("session_key")

        # frontend struggles to delete it's own cookies, let's help
        response.delete_cookie("UNICORN_ACCESS_TOKEN")
        response.delete_cookie("UNICORN_REFRESH_TOKEN")

        return response
