from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from guardian.admin import GuardedModelAdmin

from .models import Event


@admin.register(Event)
class EventAdmin(GuardedModelAdmin):
    search_fields = ["name"]

    list_display = ("name", "start_date", "visible", "active")
    list_filter = ("start_date", "visible", "active")

    readonly_fields = ("id",)

    fieldsets = (
        (None, {"fields": ("id",)}),
        (_("Key information"), {"fields": ("name", "location", ("visible", "active"))}),
        (_("Dates"), {"fields": (("start_date", "end_date"),)}),
    )

    actions = ["activate", "deactivate", "show", "hide"]

    def activate(self, request, queryset):
        updated = queryset.update(active=True)
        self.message_user(
            request,
            ngettext_lazy(
                "%d event was successfully activated.",
                "%d events was successfully activated.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    activate.short_description = _("Activate selected events")

    def deactivate(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(
            request,
            ngettext_lazy(
                "%d event was successfully deactivated.",
                "%d events was successfully deactivated.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    deactivate.short_description = _("Deactivate selected events")

    def show(self, request, queryset):
        updated = queryset.update(visible=True)
        self.message_user(
            request,
            ngettext_lazy(
                "%d event was successfully set to visible.",
                "%d events was successfully set to visible.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    show.short_description = _("Show selected events")

    def hide(self, request, queryset):
        updated = queryset.update(visible=False)
        self.message_user(
            request,
            ngettext_lazy(
                "%d event was successfully hidden.",
                "%d events was successfully hidden.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    hide.short_description = _("Hide selected events")
