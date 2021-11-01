from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from matchmaking.constants import (
    MATCH_REQUEST_LOOKING_FOR_CHOICES,
    MATCH_REQUEST_LOOKING_FOR_GROUP,
    MATCH_REQUEST_RANKS,
)
from utilities.models import CreatedUpdatedModel


class MatchRequest(CreatedUpdatedModel, models.Model):
    author = models.ForeignKey(
        verbose_name=_("author"),
        to=settings.AUTH_USER_MODEL,
        related_name="matchrequests",
        on_delete=models.CASCADE,
    )
    competition = models.ForeignKey(
        verbose_name=_("competition"),
        to="competitions.Competition",
        related_name="matchrequests",
        on_delete=models.CASCADE,
    )
    active = models.BooleanField(verbose_name=_("active"), default=True)
    text = models.TextField(verbose_name=_("description"))
    rank = models.PositiveSmallIntegerField(
        verbose_name=_("rank"), choices=MATCH_REQUEST_RANKS
    )
    role = models.TextField(verbose_name=_("role"))
    looking_for = models.PositiveSmallIntegerField(
        verbose_name=_("looking for"),
        choices=MATCH_REQUEST_LOOKING_FOR_CHOICES,
        default=MATCH_REQUEST_LOOKING_FOR_GROUP,
    )

    class Meta:
        ordering = ("-last_updated",)

    def __str__(self):
        return "{} looking for {} in {}".format(
            self.author.display_name,
            self.get_looking_for_display(),
            self.competition.name,
        )
