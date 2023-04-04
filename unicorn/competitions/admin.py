from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Competition, Contributor, Entry, File, Genre


@admin.register(Genre)
class GenreAdmin(GuardedModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)


@admin.register(Competition)
class CompetitionAdmin(GuardedModelAdmin):
    list_display = ("name", "genre", "published", "state", "entries_count")
    list_filter = ("event__name", "genre__name", "published", "state")


@admin.register(Entry)
class EntryAdmin(GuardedModelAdmin):
    list_display = ("competition", "title", "status", "contributor_count")
    list_filter = ("competition__name", "status")


@admin.register(Contributor)
class ContributorAdmin(GuardedModelAdmin):
    list_display = ("entry", "user", "extra_info")


@admin.register(File)
class FileAdmin(GuardedModelAdmin):
    list_display = ("name", "type", "entry", "active", "uploader")
    list_filter = ("entry__competition__name", "active")
