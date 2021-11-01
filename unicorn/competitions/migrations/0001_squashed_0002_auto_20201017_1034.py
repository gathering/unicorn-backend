# Generated by Django 3.1.2 on 2020-10-17 11:46

import django.contrib.postgres.fields.jsonb
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [
        ("competitions", "0001_initial"),
        ("competitions", "0002_auto_20201017_1034"),
    ]

    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Competition",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(max_length=50, unique=True, verbose_name="Name"),
                ),
                (
                    "brief_description",
                    models.CharField(
                        max_length=160, null=True, verbose_name="Brief Description"
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, default=None, null=True, verbose_name="Description"
                    ),
                ),
                ("rules", models.TextField(verbose_name="Rules")),
                (
                    "prizes",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True, default=list, null=True, verbose_name="Prizes"
                    ),
                ),
                (
                    "featured",
                    models.BooleanField(
                        default=False,
                        help_text="Competition should have extra visibility",
                        verbose_name="Featured",
                    ),
                ),
                (
                    "autoqualify",
                    models.BooleanField(
                        default=False,
                        help_text="Auto-Qualify will automatically qualify entries when they fulfill the requirements for number of contributors and extra info",
                        verbose_name="Auto-Qualify",
                    ),
                ),
                (
                    "fileupload",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True,
                        default=list,
                        null=True,
                        verbose_name="File Upload parameters",
                    ),
                ),
                (
                    "participant_limit",
                    models.PositiveSmallIntegerField(
                        default=0, null=True, verbose_name="Participant Limit"
                    ),
                ),
                (
                    "toornament",
                    models.CharField(
                        blank=True,
                        default=None,
                        max_length=128,
                        null=True,
                        verbose_name="Toornament ID",
                    ),
                ),
                (
                    "published",
                    models.BooleanField(
                        default=False,
                        help_text="Visible for regular users",
                        verbose_name="Published",
                    ),
                ),
                (
                    "report_win_loss",
                    models.BooleanField(
                        default=False,
                        help_text="Is this an externally run competition where we only report results?",
                        verbose_name="Report wins/losses",
                    ),
                ),
                ("rsvp", models.BooleanField(default=False, verbose_name="RSVP only")),
                (
                    "header_image",
                    models.URLField(
                        blank=True,
                        default=None,
                        help_text="URL to Header Image for competition.",
                        null=True,
                        verbose_name="Header Image",
                    ),
                ),
                (
                    "header_credit",
                    models.CharField(
                        blank=True,
                        default=None,
                        help_text="Required when an image is set.",
                        max_length=128,
                        null=True,
                        verbose_name="Header Image Credit",
                    ),
                ),
                (
                    "team_min",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text="Minimum number of contributors per entry.",
                        null=True,
                        verbose_name="Minimum Team Size",
                    ),
                ),
                (
                    "team_max",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text="Maximum number of contributors per entry.",
                        null=True,
                        verbose_name="Maxiumum Team Size",
                    ),
                ),
                (
                    "contributor_extra",
                    models.CharField(
                        blank=True,
                        help_text="Human readable string of which extra info, if any, is required from contributors?",
                        max_length=32,
                        null=True,
                        verbose_name="Contributor Extra Info",
                    ),
                ),
                (
                    "register_time_start",
                    models.DateTimeField(
                        blank=True,
                        default=None,
                        null=True,
                        verbose_name="Registration Start",
                    ),
                ),
                (
                    "register_time_end",
                    models.DateTimeField(
                        blank=True,
                        default=None,
                        null=True,
                        verbose_name="Registration End",
                    ),
                ),
                (
                    "run_time_start",
                    models.DateTimeField(null=True, verbose_name="Competition Start"),
                ),
                (
                    "run_time_end",
                    models.DateTimeField(null=True, verbose_name="Competition End"),
                ),
                (
                    "vote_time_start",
                    models.DateTimeField(
                        blank=True, default=None, null=True, verbose_name="Voting Start"
                    ),
                ),
                (
                    "vote_time_end",
                    models.DateTimeField(
                        blank=True, default=None, null=True, verbose_name="Voting End"
                    ),
                ),
                (
                    "show_time_start",
                    models.DateTimeField(
                        blank=True,
                        default=None,
                        null=True,
                        verbose_name="Showtime Start",
                    ),
                ),
                (
                    "show_time_end",
                    models.DateTimeField(
                        blank=True, default=None, null=True, verbose_name="Showtime End"
                    ),
                ),
                (
                    "external_url_info",
                    models.URLField(
                        blank=True,
                        default=None,
                        help_text="URL to infopage for external competition.",
                        null=True,
                        verbose_name="External URL for infopage",
                    ),
                ),
                (
                    "external_url_login",
                    models.URLField(
                        blank=True,
                        default=None,
                        help_text="URL for logging in to external competition.",
                        null=True,
                        verbose_name="External URL for login",
                    ),
                ),
                (
                    "state",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "Closed"),
                            (2, "Registration open"),
                            (4, "Registration closed"),
                            (8, "Currently Running"),
                            (16, "Closed"),
                            (32, "Voting open"),
                            (64, "Voting closed"),
                            (128, "Showtime"),
                            (256, "Finished"),
                        ],
                        default=16,
                    ),
                ),
            ],
            options={"ordering": ("genre__name", "name")},
        ),
        migrations.CreateModel(
            name="Contributor",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "extra_info",
                    models.CharField(
                        blank=True, max_length=64, null=True, verbose_name="Extra Info"
                    ),
                ),
                (
                    "is_owner",
                    models.BooleanField(default=False, verbose_name="Entry Owner"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Entry",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=45, verbose_name="Title")),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "Draft"),
                            (2, "New"),
                            (4, "Qualified"),
                            (8, "Disqualified"),
                            (16, "Not pre-selected"),
                            (32, "Invalid file"),
                        ],
                        default=1,
                        verbose_name="Status",
                    ),
                ),
                (
                    "status_comment",
                    models.TextField(
                        blank=True,
                        default=None,
                        null=True,
                        verbose_name="Status Comment",
                    ),
                ),
                (
                    "toornament",
                    models.CharField(
                        blank=True,
                        default=None,
                        max_length=128,
                        null=True,
                        verbose_name="Toornament ID",
                    ),
                ),
                (
                    "extra_info",
                    models.CharField(
                        blank=True,
                        default=None,
                        max_length=128,
                        null=True,
                        verbose_name="Extra Info",
                    ),
                ),
                (
                    "order",
                    models.PositiveSmallIntegerField(
                        default=1,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(99),
                        ],
                        verbose_name="Order",
                    ),
                ),
                (
                    "crew_msg",
                    models.CharField(
                        blank=True,
                        default=None,
                        max_length=512,
                        null=True,
                        verbose_name="Message for Crew",
                    ),
                ),
                (
                    "screen_msg",
                    models.CharField(
                        blank=True,
                        default=None,
                        max_length=140,
                        null=True,
                        verbose_name="Message for big screen",
                    ),
                ),
                (
                    "comment",
                    models.TextField(
                        blank=True, default=None, null=True, verbose_name="Comment"
                    ),
                ),
                (
                    "score",
                    models.PositiveSmallIntegerField(
                        default=0, help_text="Between 0 and 32767", verbose_name="Score"
                    ),
                ),
                (
                    "competition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="entries",
                        to="competitions.competition",
                        verbose_name="Competition",
                    ),
                ),
                (
                    "contributors",
                    models.ManyToManyField(
                        related_name="entries",
                        through="competitions.Contributor",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Contributors",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "entries",
                "ordering": ("order", "title"),
                "permissions": (
                    ("view_entry_crewmsg", "View information for crew in Entry"),
                ),
            },
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "category",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "Other"),
                            (2, "Creative"),
                            (4, "Game"),
                            (8, "Community"),
                        ],
                        default=1,
                        verbose_name="Category",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=30, unique=True, verbose_name="Name"),
                ),
            ],
            options={
                "ordering": ("name",),
                "permissions": (
                    ("create_competition", "Can create Competitions in this Genre"),
                    ("modify_all", "Can modify all Competitions in this Genre"),
                ),
                "unique_together": {("category", "name")},
            },
        ),
        migrations.CreateModel(
            name="File",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("file", models.FileField(upload_to="")),
                (
                    "mime",
                    models.CharField(
                        max_length=45, null=True, verbose_name="MIME type"
                    ),
                ),
                (
                    "type",
                    models.CharField(max_length=45, null=True, verbose_name="Type"),
                ),
                ("name", models.CharField(max_length=512, verbose_name="Name")),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "New"),
                            (2, "Preparing"),
                            (4, "Processing"),
                            (8, "Finished"),
                            (16, "Failed"),
                        ],
                        default=1,
                        verbose_name="Status",
                    ),
                ),
                ("active", models.BooleanField(default=True, verbose_name="Active")),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="files",
                        to="competitions.entry",
                        verbose_name="Entry",
                    ),
                ),
                (
                    "uploader",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Uploader",
                    ),
                ),
            ],
            options={"ordering": ("entry", "type", "-active", "name")},
        ),
        migrations.AddField(
            model_name="contributor",
            name="entry",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="entry_to_user",
                to="competitions.entry",
                verbose_name="Entry",
            ),
        ),
        migrations.AddField(
            model_name="contributor",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_to_entry",
                to=settings.AUTH_USER_MODEL,
                verbose_name="User",
            ),
        ),
        migrations.AddField(
            model_name="competition",
            name="genre",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="competitions",
                to="competitions.genre",
                verbose_name="Genre",
            ),
        ),
        migrations.CreateModel(
            name="Vote",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "score",
                    models.PositiveSmallIntegerField(
                        default=1,
                        help_text="A number between 1 and 5",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="Score",
                    ),
                ),
                ("jury", models.BooleanField(default=False, verbose_name="Jury Vote")),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="votes",
                        to="competitions.entry",
                        verbose_name="Entry",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={"unique_together": {("entry", "user")}},
        ),
        migrations.AlterField(
            model_name="competition",
            name="fileupload",
            field=models.JSONField(
                blank=True,
                default=list,
                null=True,
                verbose_name="File Upload parameters",
            ),
        ),
        migrations.AlterField(
            model_name="competition",
            name="prizes",
            field=models.JSONField(
                blank=True, default=list, null=True, verbose_name="Prizes"
            ),
        ),
    ]
