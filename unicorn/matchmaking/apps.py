from django.apps import AppConfig


class MatchmakingConfig(AppConfig):
    name = "matchmaking"

    def ready(self):
        import matchmaking.signals  # noqa: F401
