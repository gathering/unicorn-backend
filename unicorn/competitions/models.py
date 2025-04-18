import math
from datetime import datetime

import pytz
from accounts.constants import USER_ROLE_JURY
from auditlog.registry import auditlog
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, Sum
from django.utils.translation import gettext_lazy as _
from utilities.models import CreatedUpdatedModel
from utilities.utils import round_seconds

from .constants import *  # noqa: F403


class Genre(models.Model):
    category = models.CharField(
        verbose_name=_("Category"),
        max_length=16,
        choices=GENRE_CATEGORY_CHOICES,
        default=GENRE_CATEGORY_OTHER,
    )
    name = models.CharField(verbose_name=_("Name"), max_length=30, unique=True)

    class Meta:
        ordering = ("name",)
        unique_together = ["category", "name"]
        permissions = (
            ("create_competition", "Can create Competitions in this Genre"),
            ("modify_all", "Can modify all Competitions in this Genre"),
        )

    def __str__(self):
        return self.name


class Competition(CreatedUpdatedModel, models.Model):
    event = models.ForeignKey(
        to="core.Event",
        related_name="competitions",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    genre = models.ForeignKey(
        verbose_name=_("Genre"),
        to="Genre",
        related_name="competitions",
        on_delete=models.PROTECT,
    )
    name = models.CharField(verbose_name=_("Name"), max_length=50, unique=True)
    brief_description = models.CharField(verbose_name=_("Brief Description"), max_length=160, null=True)
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True, default=None)
    rules = models.TextField(verbose_name=_("Rules"))
    prizes = models.JSONField(verbose_name=_("Prizes"), null=True, blank=True, default=list)
    featured = models.BooleanField(
        verbose_name=_("Featured"),
        default=False,
        help_text=_("Competition should have extra visibility"),
    )
    autoqualify = models.BooleanField(
        verbose_name=_("Auto-Qualify"),
        default=False,
        help_text=_(
            "Auto-Qualify will automatically qualify entries when they fulfill the "
            "requirements for number of contributors and extra info"
        ),
    )
    fileupload = models.JSONField(verbose_name=_("File Upload parameters"), null=True, blank=True, default=list)
    links = models.JSONField(verbose_name=_("External links"), null=True, blank=True, default=list)
    participant_limit = models.PositiveSmallIntegerField(verbose_name=_("Participant Limit"), null=True, default=0)

    published = models.BooleanField(
        verbose_name=_("Published"),
        default=False,
        help_text=_("Visible for regular users"),
    )
    visibility = models.CharField(
        verbose_name=_("Visibility"),
        max_length=16,
        choices=COMEPTITION_VISIBILITY_CHOICES,
        default=COMPETITION_VISIBILITY_PUBLIC,
    )

    report_win_loss = models.BooleanField(
        verbose_name=_("Report wins/losses"),
        default=False,
        help_text=_("Is this an externally run competition where we only report " "results?"),
    )
    rsvp = models.BooleanField(verbose_name=_("RSVP only"), default=False)

    header_image_file = models.ImageField(
        upload_to="competition",
        verbose_name=_("Header Image File"),
        null=True,
        blank=True,
        default=None,
    )

    header_image = models.URLField(
        verbose_name=_("Header Image"),
        null=True,
        blank=True,
        default=None,
        help_text=_("URL to Header Image for competition."),
    )
    header_credit = models.CharField(
        verbose_name=_("Header Image Credit"),
        max_length=128,
        null=True,
        blank=True,
        default=None,
        help_text=_("Required when an image is set."),
    )

    sponsor_name = models.CharField(max_length=64, null=True, blank=True, default=None)
    sponsor_logo = models.ImageField(upload_to="sponsor", null=True, blank=True, default=None)

    team_min = models.PositiveSmallIntegerField(
        verbose_name=_("Minimum Team Size"),
        null=True,
        default=0,
        help_text=_("Minimum number of contributors per entry."),
    )
    team_max = models.PositiveSmallIntegerField(
        verbose_name=_("Maxiumum Team Size"),
        null=True,
        default=0,
        help_text=_("Maximum number of contributors per entry."),
    )
    contributor_extra = models.CharField(
        verbose_name=_("Contributor Extra Info"),
        max_length=32,
        null=True,
        blank=True,
        help_text=_("Human readable string of which extra info, if any, is required " "from contributors?"),
    )

    register_time_start = models.DateTimeField(
        verbose_name=_("Registration Start"), null=True, blank=True, default=None
    )
    register_time_end = models.DateTimeField(verbose_name=_("Registration End"), null=True, blank=True, default=None)
    run_time_start = models.DateTimeField(verbose_name=_("Competition Start"), null=True)
    run_time_end = models.DateTimeField(verbose_name=_("Competition End"), null=True)
    vote_time_start = models.DateTimeField(verbose_name=_("Voting Start"), null=True, blank=True, default=None)
    vote_time_end = models.DateTimeField(verbose_name=_("Voting End"), null=True, blank=True, default=None)
    show_prestart_lock = models.DateTimeField(
        verbose_name=_("Pre-show lockdown start"),
        null=True,
        blank=True,
        default=None,
        help_text=_(
            "If set, a pre-show lockdown will block all edits to the competition "
            "and related entries from the specified time to 'Showtime End'"
        ),
    )
    show_time_start = models.DateTimeField(verbose_name=_("Showtime Start"), null=True, blank=True, default=None)
    show_time_end = models.DateTimeField(verbose_name=_("Showtime End"), null=True, blank=True, default=None)

    external_url_info = models.URLField(
        verbose_name=_("External URL for infopage"),
        null=True,
        blank=True,
        default=None,
        help_text=_("URL to infopage for external competition."),
    )
    external_url_login = models.URLField(
        verbose_name=_("External URL for login"),
        null=True,
        blank=True,
        default=None,
        help_text=_("URL for logging in to external competition."),
    )

    state = models.PositiveSmallIntegerField(choices=COMPETITION_STATE_CHOICES, default=COMPETITION_STATE_CLOSED)
    scoring_complete = models.BooleanField(
        verbose_name=_("Scoring Completed"),
        default=False,
        help_text=_("Scoring is completed and the competition is ready for handing out prices"),
    )

    class Meta:
        ordering = ("genre__name", "name")

    def __str__(self):
        return self.name

    @property
    def team_required(self) -> bool:
        return bool(self.team_min and self.team_max)

    @property
    def entries_count(self) -> int:
        return self.entries.filter().count()

    @property
    def is_locked(self, time=None) -> bool:
        if not self.show_prestart_lock:
            return False

        now = time or datetime.utcnow().replace(tzinfo=pytz.utc)
        return self.show_prestart_lock < now < self.show_time_end

    def compute_state(self, time=None):
        now = time or datetime.utcnow().replace(tzinfo=pytz.utc)

        if (self.register_time_start and now < self.register_time_start) or (
            self.register_time_start is None and self.run_time_start and now < self.run_time_start
        ):
            return COMPETITION_STATE_NEW

        elif (
            self.register_time_start
            and self.register_time_end
            and self.register_time_start < now < self.register_time_end
        ):
            return COMPETITION_STATE_REG_OPEN

        elif self.register_time_end and self.run_time_start and self.register_time_end < now < self.run_time_start:
            return COMPETITION_STATE_REG_CLOSE

        elif self.run_time_start < now < self.run_time_end:
            return COMPETITION_STATE_RUN

        elif self.vote_time_start and self.vote_time_end and self.vote_time_start < now < self.vote_time_end:
            return COMPETITION_STATE_VOTE

        elif self.vote_time_end and self.show_time_start and self.vote_time_end < now < self.show_time_start:
            return COMPETITION_STATE_VOTE_CLOSED

        elif self.show_time_start and self.show_time_end and self.show_time_start < now < self.show_time_end:
            return COMPETITION_STATE_SHOW

        elif self.run_time_end < now and (
            (self.vote_time_start and now < self.vote_time_start)
            or (self.show_time_start and now < self.show_time_start)
        ):
            return COMPETITION_STATE_CLOSED

        else:
            return COMPETITION_STATE_FIN

    @property
    def next_state(self):
        return self.compute_next_state()

    # TODO: this function needs refactoring to be less complex
    def compute_next_state(self, state=None):  # noqa: C901
        state = state or self.state

        if state == COMPETITION_STATE_NEW:
            return COMPETITION_STATE_REG_OPEN if self.register_time_start else COMPETITION_STATE_RUN

        elif state == COMPETITION_STATE_REG_OPEN:
            if (self.run_time_start - self.register_time_end).seconds > 1:
                return COMPETITION_STATE_REG_CLOSE
            else:
                return COMPETITION_STATE_RUN

        elif state == COMPETITION_STATE_REG_CLOSE:
            return COMPETITION_STATE_RUN

        elif state == COMPETITION_STATE_RUN:
            if (self.vote_time_start and (self.vote_time_start - self.run_time_end).seconds > 1) or (
                self.show_time_start and (self.show_time_start - self.run_time_end).seconds > 1
            ):
                return COMPETITION_STATE_CLOSED
            elif self.vote_time_start:
                return COMPETITION_STATE_VOTE
            elif self.show_time_start:
                return COMPETITION_STATE_SHOW
            else:
                return COMPETITION_STATE_FIN

        elif state == COMPETITION_STATE_CLOSED:
            if self.vote_time_start:
                return COMPETITION_STATE_VOTE
            # implicitly means we have a show time start
            else:
                return COMPETITION_STATE_SHOW

        elif state == COMPETITION_STATE_VOTE:
            if self.show_time_start and (self.show_time_start - self.vote_time_end).seconds > 1:
                return COMPETITION_STATE_VOTE_CLOSED
            elif self.show_time_start:
                return COMPETITION_STATE_SHOW
            else:
                return COMPETITION_STATE_FIN

        elif state == COMPETITION_STATE_VOTE_CLOSED:
            return COMPETITION_STATE_SHOW if self.show_time_start else COMPETITION_STATE_FIN

        else:
            return COMPETITION_STATE_FIN

    # TODO: this function needs refactoring to be less complex
    def clean(self):  # noqa: C901
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        errors = {}

        # Validate various date ranges
        if self.register_time_start and self.register_time_end and self.register_time_start > self.register_time_end:
            errors.update({"register_time_end": _("Registration end time must be after registration start time")})
        if self.run_time_start and self.run_time_end and self.run_time_start > self.run_time_end:
            errors.update({"run_time_end": _("Competition end time must be after competition start time")})
        if self.vote_time_start and self.vote_time_end and self.vote_time_start > self.vote_time_end:
            errors.update({"vote_time_end": _("Voting end time must be after voting start time")})
        if self.show_time_start and self.show_time_end and self.show_time_start > self.show_time_end:
            errors.update({"show_time_end": _("Show end time must be after show start time")})

        if self.show_prestart_lock and not (self.show_time_start or self.show_time_end):
            errors.update(
                {
                    "show_prestart_lock": _(
                        "Pre-show lockdown start can only be set if Showtime start and end is also set."
                    )
                }
            )

        if self.show_prestart_lock and self.run_time_end and self.show_prestart_lock < self.run_time_end:
            errors.update(
                {"show_prestart_lock": _("Pre-show lockdown start cannot be before competition run time has ended.")}
            )

        # Also make sure we don't open competition backwards in time
        if not self.pk:
            if self.register_time_start and self.register_time_start < now:
                errors.update({"register_time_start": _("Registration start time cannot be in the past")})
            if self.run_time_start and self.run_time_start < now:
                errors.update({"run_time_start": _("Competition start time cannot be in the past")})
            if self.vote_time_start and self.vote_time_start < now:
                errors.update({"vote_time_start": _("Voting start time cannot be in the past")})
            if self.show_time_start and self.show_time_start < now:
                errors.update({"show_time_start": _("Show start time cannot be in the past")})

        # And now handle logic for what starts when
        if self.register_time_start and self.register_time_end and self.register_time_end > self.run_time_start:
            errors.update(
                {"register_time_end": _("Pre-registration must be finished before Competition run time starts")}
            )
        if self.vote_time_start and self.vote_time_end and self.vote_time_start < self.run_time_end:
            errors.update({"vote_time_start": _("Voting cannot open until Competition has ended")})

        # Make sure team sizes make sense
        if self.team_min and not self.team_max:
            errors.update({"team_max": _("Please also fill out Maximum Team Size")})
        if self.team_max and not self.team_min:
            errors.update({"team_min": _("Please also fill out Minimum Team Size")})
        if (self.team_min and self.team_max) and self.team_min > self.team_max:
            errors.update({"team_max": _("Maximum Team Size cannot be smaller than the minimum size")})

        # Make sure header image is credited
        if (self.header_image_file or self.header_image) and not self.header_credit:
            errors.update({"header_credit": _("Please add credit for the header image")})

        # Make sure only one of header_image_file or header_image is set
        if self.header_image_file and self.header_image:
            errors.update({"header_image": _("Please only set one of the header image fields")})

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Kill those seconds
        def r(dt):
            return round_seconds(dt, "down", 60)

        self.register_time_start = r(self.register_time_start) if self.register_time_start else None
        self.register_time_end = r(self.register_time_end) if self.register_time_end else None
        self.run_time_start = r(self.run_time_start) if self.run_time_start else None
        self.run_time_end = r(self.run_time_end) if self.run_time_end else None
        self.vote_time_start = r(self.vote_time_start) if self.vote_time_start else None
        self.vote_time_end = r(self.vote_time_end) if self.vote_time_end else None
        self.show_time_start = r(self.show_time_start) if self.show_time_start else None
        self.show_time_end = r(self.show_time_end) if self.show_time_end else None

        # Figure out which state we should be in
        self.state = self.compute_state()

        # run parent logic
        super(Competition, self).save(*args, **kwargs)


auditlog.register(Competition)


class Entry(CreatedUpdatedModel, models.Model):
    competition = models.ForeignKey(
        verbose_name=_("Competition"),
        to="Competition",
        related_name="entries",
        on_delete=models.PROTECT,
    )
    contributors = models.ManyToManyField(
        verbose_name=_("Contributors"),
        to="accounts.User",
        through="Contributor",
        related_name="entries",
    )
    title = models.CharField(verbose_name=_("Title"), max_length=45)
    status = models.PositiveSmallIntegerField(
        verbose_name=_("Status"),
        choices=ENTRY_STATUS_CHOICES,
        default=ENTRY_STATUS_DRAFT,
    )
    status_comment = models.TextField(verbose_name=_("Status Comment"), blank=True, null=True, default=None)
    extra_info = models.CharField(
        verbose_name=_("Extra Info"),
        max_length=128,
        blank=True,
        null=True,
        default=None,
    )
    order = models.PositiveSmallIntegerField(
        verbose_name=_("Order"),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(99)],
    )

    crew_msg = models.CharField(
        verbose_name=_("Message for Crew"),
        max_length=512,
        blank=True,
        null=True,
        default=None,
    )
    screen_msg = models.CharField(
        verbose_name=_("Message for big screen"),
        max_length=140,
        blank=True,
        null=True,
        default=None,
    )
    vote_msg = models.CharField(
        verbose_name=_("Message for voting"),
        max_length=140,
        blank=True,
        null=True,
        default=None,
    )

    comment = models.TextField(verbose_name=_("Comment"), blank=True, null=True, default=None)
    score = models.PositiveSmallIntegerField(verbose_name=_("Score"), default=0, help_text=_("Between 0 and 32767"))

    class Meta:
        ordering = ("order", "title")
        verbose_name_plural = "entries"
        permissions = (("view_entry_crewmsg", "View information for crew in Entry"),)

    def __str__(self):
        return _("%(title)s in %(competition)s") % {
            "title": self.title,
            "competition": self.competition.name,
        }

    @property
    def contributor_count(self) -> int:
        return self.contributors.filter().count()

    def update_score(self):
        self.score = self.votesum()
        self.save()

    def votesum(self) -> float:
        mortal_weight = 0.7
        jury_weight = 1 - mortal_weight

        # Sum up the vote scores from non-jury votes on this entry, and return 0 if there is none
        mortal_score = Vote.objects.filter(Q(entry=self), Q(jury=False)).aggregate(Sum("score"))["score__sum"] or 0

        # Sum all vote scores for the current competition
        mortal_sum = (
            Vote.objects.filter(Q(entry__competition=self.competition), Q(jury=False)).aggregate(Sum("score"))[
                "score__sum"
            ]
            or 0
        )
        jury_sum = (
            Vote.objects.filter(Q(entry__competition=self.competition), Q(jury=True)).aggregate(Sum("score"))[
                "score__sum"
            ]
            or 0
        )

        # Calculate the vote score from jury votes on this entry
        if jury_sum:
            jury_self = Vote.objects.filter(Q(entry=self), Q(jury=True)).aggregate(Sum("score"))["score__sum"] or 0
            jury_score = jury_self * (((mortal_sum / mortal_weight) * jury_weight) / jury_sum)
        else:
            jury_score = 0

        return math.floor((jury_score + mortal_score) + 0.5)

    def validate_contributors(self) -> bool:
        if self.contributor_count < 1 or (
            self.competition.contributor_extra
            and Contributor.objects.filter(
                Q(entry_id=self.pk),
                Q(extra_info__isnull=True) | Q(extra_info__exact=""),
            ).exists()
        ):
            return False

        return True

    def clean(self):
        errors = {}
        if not self.competition.published:
            errors.update({"competition": "This competition is not currently available for entry registrations!"})

        if (
            not self.pk
            and self.competition.participant_limit
            and self.competition.entries_count >= self.competition.participant_limit
        ):
            errors.update({"competition": "This competition is currently full!"})

        if not self.pk:
            if (self.competition.state != COMPETITION_STATE_REG_OPEN and self.competition.register_time_start) or (
                self.competition.state != COMPETITION_STATE_RUN and not self.competition.register_time_start
            ):
                errors.update({"competition": "Registrations are closed for this competition!"})

        if errors:
            raise ValidationError(errors)


class Contributor(models.Model):
    entry = models.ForeignKey(
        verbose_name=_("Entry"),
        to="Entry",
        on_delete=models.CASCADE,
        related_name="entry_to_user",
    )
    user = models.ForeignKey(
        verbose_name=_("User"),
        to="accounts.User",
        on_delete=models.CASCADE,
        related_name="user_to_entry",
    )
    extra_info = models.CharField(verbose_name=_("Extra Info"), max_length=64, blank=True, null=True)
    is_owner = models.BooleanField(verbose_name=_("Entry Owner"), default=False)

    def clean(self):
        errors = {}
        try:
            exists = Contributor.objects.get(entry=self.entry, user=self.user)
        except ObjectDoesNotExist:
            pass
        else:
            if (self.pk and self.pk != exists.pk) or (not self.pk and exists):
                errors.update({"user": "This user is already a contributor to selected entry!"})

        if self.entry.status not in (ENTRY_STATUS_DRAFT, ENTRY_STATUS_NEW) and (
            self.entry.competition.contributor_extra and not self.extra_info
        ):
            errors.update({"extra_info": "Extra info is required in this competition"})

        if errors:
            raise ValidationError(errors)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # saving a file as active will forcibly make the last one not active
        if self.is_owner:
            try:
                old_owner = Contributor.objects.get(Q(entry=self.entry), Q(is_owner=True))
                if self.pk and self.pk is not old_owner.pk:
                    old_owner.is_owner = False
                    old_owner.save()
            except ObjectDoesNotExist:
                pass

        super(Contributor, self).save(force_insert, force_update, using, update_fields)


class File(CreatedUpdatedModel, models.Model):
    entry = models.ForeignKey(
        verbose_name=_("Entry"),
        to="Entry",
        on_delete=models.CASCADE,
        related_name="files",
    )
    uploader = models.ForeignKey(
        verbose_name=_("Uploader"),
        to="accounts.User",
        on_delete=models.SET_NULL,
        null=True,
    )

    file = models.FileField()
    mime = models.CharField(verbose_name=_("MIME type"), max_length=45, null=True)
    type = models.CharField(verbose_name=_("Type"), max_length=45, null=True)

    name = models.CharField(verbose_name=_("Name"), max_length=512)
    status = models.PositiveSmallIntegerField(
        verbose_name=_("Status"), choices=FILE_STATUS_CHOICES, default=FILE_STATUS_NEW
    )
    active = models.BooleanField(verbose_name=_("Active"), default=True)

    class Meta:
        ordering = ("entry", "type", "-active", "name")

    def __str__(self):
        return self.name

    def clean(self):
        errors = {}

        # verify that we are using a valid type, based on definitions on competition
        allowed_types = []
        for t in self.entry.competition.fileupload:
            allowed_types.append(t["type"])
        if self.type not in allowed_types:
            errors.update({"type": "Specified type is not permitted for this competition"})

        if (
            not self.uploader.has_perm("competitions.view_entry_crewmsg")
            and self.uploader not in self.entry.contributors.all()
        ):
            errors.update({"uploader": "Only contributors can upload files to entries"})

        if errors:
            raise ValidationError(errors)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # saving a file as active will forcibly make the last one not active
        if self.active:
            try:
                old_file = File.objects.get(Q(entry=self.entry), Q(type=self.type), Q(active=True))
                old_file.active = False
                old_file.save()
            except ObjectDoesNotExist:
                pass

        super(File, self).save(force_insert, force_update, using, update_fields)


class Vote(models.Model):
    entry = models.ForeignKey(
        verbose_name=_("Entry"),
        to="Entry",
        related_name="votes",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(verbose_name=_("User"), to="accounts.User", on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(
        verbose_name=_("Score"),
        help_text=_("A number between 1 and 5"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1,
    )
    jury = models.BooleanField(verbose_name=_("Jury Vote"), default=False)

    class Meta:
        unique_together = ("entry", "user")

    def clean(self):
        errors = {}
        try:
            exists = Vote.objects.get(entry=self.entry, user=self.user)
        except ObjectDoesNotExist:
            pass
        else:
            if (self.pk and self.pk != exists.pk) or (not self.pk and exists):
                errors.update(
                    {
                        "entry": "User has already voted on this entry! (ID: {}) Please update "
                        "existing vote object insted on creating a new.".format(exists.pk)
                    }
                )

        if self.entry.competition.state != COMPETITION_STATE_VOTE:
            errors.update({"entry": "It is not possible to vote in this entry now"})

        if self.user in self.entry.contributors.all():
            errors.update({"user": "You cannot vote on entries you have contributed to"})

        if errors:
            raise ValidationError(errors)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # set jury field based on user role
        if self.user.role == USER_ROLE_JURY:
            self.jury = True
        else:
            self.jury = False

        # call super save method
        super(Vote, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
