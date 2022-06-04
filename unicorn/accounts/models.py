import uuid
from datetime import date

import requests
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from guardian.mixins import GuardianUserMixin

from .constants import (
    USER_DISPLAY_CHOICES,
    USER_DISPLAY_FIRST_LAST,
    USER_GENDERS,
    USER_ROLE_CHOICES,
    USER_ROLE_MORTAL,
)


class User(AbstractUser, GuardianUserMixin):
    uuid = models.UUIDField(
        verbose_name=_("UUID"), default=uuid.uuid4, editable=False, primary_key=True
    )
    role = models.CharField(
        verbose_name=_("Role"),
        max_length=16,
        choices=USER_ROLE_CHOICES,
        default=USER_ROLE_MORTAL,
    )
    username_overridden = models.BooleanField(
        default=False,
        help_text=_(
            "User has manually set a custom username. This will stop automatic updates from social providers."
        ),
    )
    display_name_format = models.CharField(
        verbose_name=_("Display Name format"),
        max_length=3,
        choices=USER_DISPLAY_CHOICES,
        default=USER_DISPLAY_FIRST_LAST,
    )
    phone_number = models.CharField(
        verbose_name=_("Phone Number"),
        validators=[
            RegexValidator(
                regex=r"^\+[1-9]\d{1,14}$",
                message=_(
                    "Phone Number must be entered in valid E.164 format (international with + prefix). "
                    "Up to 15 digits allowed."
                ),
            )
        ],
        max_length=16,
        blank=True,
        null=True,
        help_text=_(
            "Must be in valid E.164 format (international with + prefix). Up to 15 digits allowed."
        ),
    )
    zip = models.CharField(
        verbose_name=_("Zip Code"), max_length=16, blank=True, null=True
    )
    birth = models.DateField(
        verbose_name=_("Birth Date"),
        default=None,
        blank=True,
        null=True,
        help_text=_("ISO 8601 date format."),
    )
    gender = models.CharField(
        verbose_name=_("Gender"),
        max_length=6,
        choices=USER_GENDERS,
        blank=True,
        null=True,
        default=None,
    )
    approved_for_pii = models.BooleanField(
        verbose_name=_("Approved for PII"),
        default=False,
        help_text=_(
            "User is approved for interacting with PII data on other accounts."
        ),
    )
    accepted_location = models.BooleanField(
        verbose_name=_("Has accepted location tracking"), default=False
    )
    row = models.PositiveSmallIntegerField(
        verbose_name=_("row"), null=True, blank=True, validators=[MinValueValidator(1)]
    )
    seat = models.PositiveSmallIntegerField(
        verbose_name=_("seat"), null=True, blank=True, validators=[MinValueValidator(1)]
    )
    checked_in = models.BooleanField(
        verbose_name=_("checked in"),
        default=False,
        help_text=_(
            "Designates whether the user has been physically checked in to the event or not."
        ),
    )
    crew = models.JSONField(verbose_name=_("crew details"), null=True, blank=True)

    class Meta:
        ordering = ("last_name", "first_name")

    def __str__(self):
        return f"{self.display_name} ({self.uuid})"

    @property
    def id(self):
        return self.uuid

    @property
    def display_name(self) -> str:
        return self.get_display_name_format_display() % {
            "first": self.first_name,
            "last": self.last_name,
            "nick": self.username,
        }

    @property
    def age(self):
        if not self.birth:
            return None

        try:
            return relativedelta(date.today(), self.birth).years or None
        except TypeError:
            # this happens if birth is set as a string and we try to get age
            # without refetching from database to get the actual date object
            return None


class UserCardManager(models.Manager):
    def get(self, *args, **kwargs):
        try:
            card = super(UserCardManager, self).get(*args, **kwargs)
        except ObjectDoesNotExist:
            value = (
                kwargs.get("value__iexact")
                if kwargs.get("value__iexact")
                else kwargs.get("value")
            )
            card = self.fetch_from_wannabe(value)

        if not card:
            return None

        return card

    def fetch_from_wannabe(self, card):
        app = ""
        key = ""

        payload = {"app": app, "apikey": key, "card_number": str(card)}

        r = requests.get(
            "https://wannabe.gathering.org/tg19/api/Badge/check_user_id_by_card_number",
            params=payload,
        )

        data = r.json()
        if not data["status"]:
            return None

        uid = data["user_id"]
        oscar_url = "accounts/wannabeidmapper/"
        r = requests.post(oscar_url, json={"id": uid})
        if not r.status_code == 200:
            return None

        try:
            user = User.objects.get(pk=r.json()["user"])
        except ObjectDoesNotExist:
            return None

        return self.create(user=user, value=card)


class UserCard(models.Model):
    user = models.ForeignKey(
        to=User, related_name="usercards", on_delete=models.CASCADE
    )
    value = models.CharField(max_length=16, unique=True)

    class Meta:
        ordering = ("user", "value")

    def __str__(self):
        return "{} for user {}".format(self.value, self.user.display_name)


class AutoCrew(models.Model):
    crew = models.CharField(max_length=128, db_index=True)
    group = models.ForeignKey(
        to=Group, related_name="autocrews", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ("crew",)

    def __str__(self):
        return "{} to group {}".format(self.crew, self.group.name)
