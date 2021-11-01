from achievements.models import (
    Achievement,
    Award,
    Category,
    Level,
    NfcScan,
    NfcStation,
    Team,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from utilities.api import ModelViewSet

from . import serializers
from .. import filters

#
# Teams
#


class TeamViewSet(ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = serializers.TeamSerializer


#
# Categories
#


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer

    filterset_class = filters.CategoryFilter


class LevelViewSet(ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = serializers.LevelSerializer

    filterset_class = filters.LevelFilter

    @action(detail=True, methods=["patch"])
    def seen(self, request, pk=None):
        obj = self.get_object()
        obj.seen_now()
        obj.save()

        return Response(
            serializers.LevelSerializer(instance=obj, context={"request": request}).data
        )

    @action(detail=True, methods=["patch"])
    def delivered(self, request, pk=None):
        obj = self.get_object()
        obj.delivered_now()
        obj.save()

        return Response(
            serializers.LevelSerializer(instance=obj, context={"request": request}).data
        )


#
# Achievements
#


class AchievementViewSet(ModelViewSet):
    queryset = Achievement.objects.select_related("category")
    serializer_class = serializers.AchievementSerializer

    filterset_class = filters.AchievementFilter

    @action(detail=True)
    def users(self, request, pk=None):
        achievement = self.get_object()

        if achievement.awards:
            # all users with this achievement
            return
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


class AwardViewSet(ModelViewSet):
    queryset = Award.objects.all()
    serializer_class = serializers.AwardSerializer


class NfcStationViewSet(ModelViewSet):
    queryset = NfcStation.objects.all()
    serializer_class = serializers.NfcStationSerializer


class NfcScanViewSet(ModelViewSet):
    queryset = NfcScan.objects.all()
    serializer_class = serializers.NfcScanSerializer
