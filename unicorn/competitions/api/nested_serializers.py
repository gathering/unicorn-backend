from competitions.constants import GENRE_CATEGORY_CHOICES
from competitions.models import Competition, Entry, File, Genre
from rest_framework import serializers
from utilities.api import ChoiceField, WritableNestedSerializer

#
# Genre
#


class NestedGenreSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="competitions-api:genre-detail"
    )
    category = ChoiceField(choices=GENRE_CATEGORY_CHOICES)

    class Meta:
        model = Genre
        fields = ("obj_type", "id", "url", "category", "name")
        read_only_fields = ("category", "name")


#
# Competition
#


class NestedCompetitionSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="competitions-api:competition-detail"
    )

    class Meta:
        model = Competition
        fields = ("obj_type", "id", "url", "name", "brief_description", "state")
        read_only_fields = ["name", "brief_description", "state"]


#
# Entry
#


class NestedEntrySerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="competitions-api:entry-detail"
    )
    is_contributor = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = ["obj_type", "id", "url", "title", "is_contributor"]

    def get_is_contributor(self, obj):
        if not self.context["request"].user.is_authenticated:
            return False

        if obj in self.context["request"].user.entries.all():
            return True

        return False


class NestedFileVoteSerializer(WritableNestedSerializer):
    kind = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = ("type", "name", "kind", "url")

    def get_kind(self, obj):
        fileupload = obj.entry.competition.fileupload
        for kind in fileupload:
            if kind.get("type", None) == obj.type:
                return kind.get("file", None)

        return None

    def get_url(self, obj):
        request = self.context.get("request")
        file_url = obj.file.url
        return request.build_absolute_uri(file_url)
