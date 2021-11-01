from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import MatchRequest


class MatchmakingAdmin(GuardedModelAdmin):
    list_display = ("author", "competition", "active", "rank", "role")


admin.site.register(MatchRequest, MatchmakingAdmin)
