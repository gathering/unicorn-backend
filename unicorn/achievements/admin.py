from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Achievement, Award, Category, NfcScan, NfcStation, Team


class AchievementAdmin(GuardedModelAdmin):
    list_display = (
        "category",
        "name",
        "requirement",
        "hidden",
        "multiple",
        "manual_validation",
    )
    list_filter = ("category", "hidden", "manual_validation")

    readonly_fields = ("manual_validation",)

    fields = (
        "category",
        ("name", "points", "icon"),
        "requirement",
        ("type", "multiple", "hidden"),
        "manual_validation",
        "qs_award",
    )


class AwardAdmin(GuardedModelAdmin):
    list_display = ("achievement", "user", "seen", "created")
    list_filter = ("seen",)

    readonly_fields = ("created",)

    fields = ("achievement", "user", "seen", *readonly_fields)


class NfcScanAdmin(GuardedModelAdmin):
    list_display = ("created", "station", "get_card", "get_user")
    list_filter = ("station",)
    ordering = ("-created",)

    def get_card(self, obj):
        return obj.usercard.value

    get_card.short_description = "Card Value"
    get_card.admin_order_field = "usercard"

    def get_user(self, obj):
        return obj.usercard.user.display_name

    get_user.short_description = "User"
    get_user.admin_order_field = "usercard__user"


# Register your models here.
admin.site.register(Category)
admin.site.register(Achievement, AchievementAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(NfcStation)
admin.site.register(NfcScan, NfcScanAdmin)
admin.site.register(Team)
