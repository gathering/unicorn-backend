from datetime import datetime

from accounts.models import UserCard
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from guardian.shortcuts import assign_perm, remove_perm
from multiselectfield import MultiSelectField as OriginalMultiSelectField
from utilities.models import CreatedUpdatedModel

from .constants import *  # noqa: F403

User = get_user_model()


class MultiSelectField(OriginalMultiSelectField):
    def get_prep_value(self, value):
        return "" if value is None else ",".join(str(s) for s in value)


class Team(models.Model):
    name = models.CharField(verbose_name=_("team"), max_length=30)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    @property
    def user_count(self) -> int:
        return self.users.count()

    @property
    def score(self) -> int:
        points = Award.objects.filter(
            models.Q(user__in=models.Subquery(self.users.all().values("id")))
        ).aggregate(models.Sum("achievement__points"))["achievement__points__sum"]

        return points if points else 0


class Category(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=30)
    levels = models.JSONField(verbose_name=_("Levels"), default=list)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Level(models.Model):
    category = models.ForeignKey(
        verbose_name=_("category"),
        to=Category,
        related_name="userlevels",
        on_delete=models.PROTECT,
    )
    user = models.ForeignKey(
        verbose_name=_("user"),
        to=settings.AUTH_USER_MODEL,
        related_name="userlevels",
        on_delete=models.CASCADE,
    )
    level = models.IntegerField(verbose_name=_("level"))
    seen = models.DateTimeField(null=True, default=None, blank=True)
    delivered = models.DateTimeField(null=True, default=None, blank=True)

    class Meta:
        unique_together = ("user", "category", "level")

    def seen_now(self):
        self.seen = datetime.now()

    def delivered_now(self):
        self.delivered = datetime.now()

    def clean(self):
        if self.level > len(self.category.levels) - 1:
            raise ValidationError(
                {"level": "This category does not have that many levels!"}
            )


class Achievement(models.Model):
    category = models.ForeignKey(
        verbose_name=_("Category"),
        to="Category",
        related_name="achievements",
        on_delete=models.PROTECT,
    )
    users = models.ManyToManyField(
        verbose_name=_("Users"), to="accounts.User", through="Award"
    )
    name = models.CharField(verbose_name=_("Name"), max_length=50, unique=True)
    icon = models.CharField(
        verbose_name=_("Icon"),
        max_length=25,
        blank=True,
        null=True,
        default=None,
        help_text=_("Font Awesome icon class (fa-xxxx)."),
    )
    requirement = models.TextField(
        verbose_name=_("Requirement"),
        help_text=_(
            "Human friendly what needs to be done in order to be awarded this achievement. "
            "This is used to aid both users trying to achieve it and admins when awarding."
        ),
    )
    manual_validation = models.BooleanField(
        verbose_name=_("Manual validation"),
        default=True,
        help_text=_(
            "Requires manual validation to be awarded. This will be automatically set based "
            "on the contents of Award QuerySet."
        ),
    )
    points = models.PositiveSmallIntegerField(
        verbose_name=_("Points"), help_text=_("Between 0 and 32767")
    )
    multiple = models.BooleanField(
        verbose_name=_("Multiple"),
        help_text=_(
            "Allow users to be awarded this achievement multiple times. Allowed intervals "
            "should be written in the requirement field to help users and aid when manual "
            "validation is active."
        ),
    )
    hidden = models.BooleanField(
        verbose_name=_("Hidden"),
        help_text=_(
            "Hide the details of this Achievement until the user has been awarded it."
        ),
    )
    type = MultiSelectField(choices=ACHIEVEMENT_TYPE_CHOICES, null=True, default=None)

    qs_award = models.TextField(
        verbose_name=_("Award QuerySet"),
        null=True,
        default=None,
        blank=True,
        help_text=_(
            "The contents of this field - when run - should return a queryset with "
            "all users which this achievement should be awarded."
        ),
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.qs_award:
            self.manual_validation = True
        else:
            self.manual_validation = False

        if not self.pk:
            created = True
        else:
            created = False

        super(Achievement, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        if created:
            g = Group.objects.get(name="p-achievement-admin")
            assign_perm("view_achievement", g, self)
            assign_perm("change_achievement", g, self)
            assign_perm("delete_achievement", g, self)

        try:
            g = Group.objects.get(name="p-anonymous")

            if self.hidden:
                remove_perm("view_achievement", g, self)

            else:
                assign_perm("view_achievement", g, self)

        except Group.DoesNotExist:
            pass


class Award(models.Model):
    created = models.DateTimeField(verbose_name=_("Created"), auto_now_add=True)
    achievement = models.ForeignKey(
        verbose_name=_("Achivement"),
        to="Achievement",
        related_name="awards",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name=_("User"),
        to="accounts.User",
        related_name="awards",
        on_delete=models.CASCADE,
    )
    seen = models.BooleanField(verbose_name=_("Seen"), default=False)

    class Meta:
        ordering = ("achievement", "user")

    def __str__(self):
        return _("%(achievement)s to %(user)s") % {
            "achievement": self.achievement.name,
            "user": self.user.uuid,
        }

    def clean(self):
        errors = {}
        if not self.achievement.multiple:
            try:
                exists = Award.objects.get(user=self.user, achievement=self.achievement)
                if (self.pk and self.pk != exists.pk) or (not self.pk and exists):
                    errors.update(
                        {"user": "This user has already been awarded this achievement."}
                    )
            except Award.DoesNotExist:
                pass

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.clean()
        super(Award, self).save(*args, **kwargs)

        assign_perm("view_award", self.user, self)


class NfcStation(models.Model):
    name = models.CharField(verbose_name=_("Station Name"), max_length=32, unique=True)

    def __str__(self):
        return self.name


class NfcScan(CreatedUpdatedModel, models.Model):
    station = models.ForeignKey(
        verbose_name=_("Station"),
        to=NfcStation,
        related_name="scans",
        on_delete=models.PROTECT,
    )
    usercard = models.ForeignKey(
        verbose_name=_("Usercard"),
        to=UserCard,
        related_name="scans",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "{} at {} at {}".format(self.usercard, self.station, self.created)

    def save(self, *args, **kwargs):
        super(NfcScan, self).save(*args, **kwargs)

        assign_perm("view_nfcscan", self.usercard.user, self)
