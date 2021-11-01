from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from utilities.models import CreatedUpdatedModel


class Thread(CreatedUpdatedModel, models.Model):
    title = models.CharField(verbose_name=_("title"), max_length=50)
    users = models.ManyToManyField(
        verbose_name=_("users"),
        to=settings.AUTH_USER_MODEL,
        through="ThreadMember",
        related_name="threads",
    )

    class Meta:
        ordering = ("-last_updated",)


class ThreadMember(models.Model):
    thread = models.ForeignKey(
        verbose_name=_("thread"), to="Thread", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        verbose_name=_("user"), to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    seen = models.DateTimeField(verbose_name=_("last seen"))
    favorite = models.BooleanField(verbose_name=_("favorite"))

    class Meta:
        unique_together = ("thread", "user")


class Message(CreatedUpdatedModel, models.Model):
    thread = models.ForeignKey(
        verbose_name=_("parent thread"),
        to="Thread",
        related_name="messages",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        verbose_name=_("author"),
        to=settings.AUTH_USER_MODEL,
        related_name="messages",
        on_delete=models.SET_NULL,
        null=True,
    )
    content = models.TextField(verbose_name=_("message contents"))

    class Meta:
        ordering = ("-last_updated",)
