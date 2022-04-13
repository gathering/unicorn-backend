from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy

from .models import AutoCrew, User


@admin.register(User)
class ExtendedUserAdmin(UserAdmin):
    search_fields = ["first_name", "last_name", "username", "email"]
    readonly_fields = (
        "uuid",
        "approved_for_pii",
        "accepted_location",
        "checked_in",
        "crew",
        "row",
        "seat",
        "is_superuser",
        "is_staff",
        "is_active",
    )
    list_display = (
        "username",
        "last_name",
        "first_name",
        "email",
        "display_name",
        "is_active",
        "is_staff",
        "approved_for_pii",
    )
    list_filter = (
        "checked_in",
        "approved_for_pii",
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    ("username", "username_overridden"),
                    "password",
                    ("accepted_location", "approved_for_pii"),
                )
            },
        ),
        (
            _("Personal info"),
            {
                "fields": (
                    ("first_name", "last_name"),
                    "email",
                    "phone_number",
                    "zip",
                    ("birth", "gender"),
                )
            },
        ),
        (
            _("Event related info"),
            {
                "fields": (
                    "display_name_format",
                    ("row", "seat"),
                    "checked_in",
                    "crew",
                    "role",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": (("last_login", "date_joined"),)}),
    )

    actions = ["disable", "enable"]

    def disable(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            ngettext_lazy(
                "%d user was successfully disabled.",
                "%d users were successfully disabled.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    disable.short_description = _("Disable selected users")

    def enable(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            ngettext_lazy(
                "%d user was successfully enabled.",
                "%d users were successfully enabled.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    enable.short_description = _("Enable selected users")


@admin.register(AutoCrew)
class AutoCrewAdmin(admin.ModelAdmin):
    pass
