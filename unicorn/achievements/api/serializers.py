from accounts.api.nested_serializers import NestedUserSerializer
from accounts.models import UserCard
from achievements.models import (
    Achievement,
    Award,
    Category,
    Level,
    NfcScan,
    NfcStation,
    Team,
)
from django.db.models import Q, Sum
from rest_framework import serializers
from utilities.api import ValidatedModelSerializer, WritableNestedSerializer

from . import nested_serializers
from ..constants import ACHIEVEMENT_TYPE_CHOICES

#
# Teams
#


class TeamSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="achievements-api:team-detail")
    top_players = serializers.SerializerMethodField()

    class Meta:
        model = Team
        read_only_fields = (
            "obj_type",
            "url",
            "id",
            "user_count",
            "score",
            "top_players",
        )
        fields = (*read_only_fields, "name")

    def get_top_players(self, obj):
        data = []
        users = (
            obj.users.filter(Q(awards__isnull=False))
            .distinct()
            .annotate(points=Sum("awards__achievement__points"))
            .order_by("-points")
        )
        for u in users[:5]:
            data.append({"user": u.display_name, "points": u.points})

        return data


#
# Categories
#


class CategorySerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="achievements-api:category-detail"
    )

    class Meta:
        model = Category
        fields = ("obj_type", "url", "id", "name", "levels")


class NestedCategorySerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="achievements-api:category-detail"
    )

    class Meta:
        model = Category
        fields = ("obj_type", "url", "id", "name", "levels")


class LevelSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="achievements-api:level-detail"
    )
    category = nested_serializers.NestedCategorySerializer()

    class Meta:
        model = Level
        fields = (
            "obj_type",
            "url",
            "id",
            "category",
            "user",
            "level",
            "seen",
            "delivered",
        )


#
# Achievements
#


class AchievementAwardSerializer(serializers.HyperlinkedModelSerializer):
    user = NestedUserSerializer()

    class Meta:
        model = Award
        fields = ("user", "created")


class AchievementSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="achievements-api:achievement-detail"
    )
    category = NestedCategorySerializer()
    type = serializers.MultipleChoiceField(choices=ACHIEVEMENT_TYPE_CHOICES)

    my_award_count = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        read_only_fields = (
            "obj_type",
            "url",
            "id",
            "manual_validation",
            "my_award_count",
        )
        fields = (
            *read_only_fields,
            "category",
            "name",
            "icon",
            "requirement",
            "points",
            "multiple",
            "hidden",
            "type",
        )

    def get_my_award_count(self, obj) -> int:
        request = self.context.get("request")
        if not request and not request.user.is_authenticated:
            return 0

        count = obj.awards.filter(user=request.user).count()
        return count


class NestedAchievementSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="achievements-api:achievement-detail"
    )

    class Meta:
        model = Achievement
        fields = ("obj_type", "id", "url", "name")


#
# Awards
#


class AwardSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="achievements-api:award-detail"
    )
    user = NestedUserSerializer()
    achievement = NestedAchievementSerializer()

    class Meta:
        model = Award
        fields = ("obj_type", "url", "id", "user", "achievement", "created")


#
# NFC
#


class NfcStationSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="achievements-api:nfcstation-detail"
    )

    class Meta:
        model = NfcStation
        fields = ("obj_type", "url", "id", "name")


class NestedNfcStationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="achievements-api:nfcstation-detail"
    )

    class Meta:
        model = NfcStation
        fields = ("obj_type", "url", "id", "name")


class NfcScanSerializer(serializers.ModelSerializer):
    usercard = serializers.CharField()

    class Meta:
        model = NfcScan
        fields = ("id", "station", "usercard", "created")

    def create(self, validated_data):
        try:
            usercard = UserCard.objects.get(value=validated_data["usercard"])
        except UserCard.DoesNotExist:
            raise serializers.ValidationError({"usercard": "Usercard was not found"})

        scan = NfcScan.objects.create(
            station=validated_data["station"], usercard=usercard
        )
        return scan
