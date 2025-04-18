import re

from accounts.api.nested_serializers import (
    NestedUserSerializer,
    NestedUserWithDetailsSerializer,
)
from competitions.constants import (
    COMPETITION_STATE_CHOICES,
    ENTRY_STATUS_CHOICES,
    ENTRY_STATUS_NEW,
    GENRE_CATEGORY_CHOICES,
)
from competitions.models import Competition, Contributor, Entry, File, Genre, Vote
from drf_spectacular.utils import extend_schema_field
from guardian.shortcuts import assign_perm
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.utils import model_meta
from utilities.api import (
    ChoiceField,
    ValidatedModelSerializer,
    WritableNestedSerializer,
)

from .nested_serializers import (
    NestedCompetitionSerializer,
    NestedEntrySerializer,
    NestedFileVoteSerializer,
    NestedGenreSerializer,
)

#
# Genres
#


class GenreSerializer(ValidatedModelSerializer):
    category = ChoiceField(choices=GENRE_CATEGORY_CHOICES)

    class Meta:
        model = Genre
        fields = ("obj_type", "permissions", "id", "category", "name")


#
# Files
#


class FileSerializer(ValidatedModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = (
            "obj_type",
            "permissions",
            "id",
            "url",
            "name",
            "type",
            "status",
            "active",
        )

    def get_url(self, file) -> str:
        request = self.context.get("request")
        file_url = file.file.url
        return request.build_absolute_uri(file_url)

    def create(self, validated_data):
        instance = super(FileSerializer, self).create(validated_data)

        # assign permissions
        assign_perm("change_file", self.context["request"].user, instance)
        assign_perm("delete_file", self.context["request"].user, instance)

        return instance


#
# Competitions
#


class CompetitionSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="competitions-api:competition-detail")
    genre = NestedGenreSerializer()
    state = ChoiceField(choices=COMPETITION_STATE_CHOICES, read_only=True)
    next_state = ChoiceField(choices=COMPETITION_STATE_CHOICES, read_only=True)
    entries = NestedEntrySerializer(many=True, read_only=True)

    def __init__(self, *args, **kwargs):
        super(CompetitionSerializer, self).__init__(*args, **kwargs)

        if self.context.get("request") and not self.context["request"].user.has_perm("view_entry"):
            self.fields.pop("entries")

    class Meta:
        model = Competition
        fields = [
            "obj_type",
            "permissions",
            "id",
            "url",
            "genre",
            "name",
            "brief_description",
            "description",
            "rules",
            "prizes",
            "fileupload",
            "links",
            "participant_limit",
            "published",
            "visibility",
            "report_win_loss",
            "rsvp",
            "header_image_file",
            "header_image",
            "header_credit",
            "sponsor_name",
            "sponsor_logo",
            "team_min",
            "team_max",
            "contributor_extra",
            "external_url_info",
            "external_url_login",
            "state",
            "entries_count",
            "entries",
            "register_time_start",
            "register_time_end",
            "run_time_start",
            "run_time_end",
            "vote_time_start",
            "vote_time_end",
            "show_prestart_lock",
            "show_time_start",
            "show_time_end",
            "team_required",
            "created",
            "last_updated",
            "next_state",
            "featured",
            "autoqualify",
            "scoring_complete",
        ]

    def create(self, validated_data):
        instance = super(CompetitionSerializer, self).create(validated_data)

        # assign permissions
        assign_perm("change_competition", self.context["request"].user, instance)
        assign_perm("delete_competition", self.context["request"].user, instance)

        return instance

    def update(self, instance, validated_data):
        # stop update if compo is locked
        if instance.is_locked:
            raise ValidationError(
                {"error": "This competition is currently locked down pending stage show, and no edits are permitted."}
            )

        return super(CompetitionSerializer, self).update(instance, validated_data)


#
# Entries
#


class EntryContributorSerializer(WritableNestedSerializer):
    user = serializers.SerializerMethodField(read_only=True, source="user")

    class Meta:
        model = Contributor
        fields = ("obj_type", "id", "user", "extra_info", "is_owner")

    @extend_schema_field(NestedUserSerializer)  # TODO: maybe redo this method to return the same schema in all cases?
    def get_user(self, instance, **kwargs):
        request = self.context.get("request", None)
        if request and request.user.has_perm("competitions.view_entry_crewmsg"):
            return NestedUserWithDetailsSerializer(instance=instance.user).data
        else:
            return NestedUserSerializer(instance=instance.user).data


class EntrySerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="competitions-api:entry-detail")
    competition = NestedCompetitionSerializer()
    status = ChoiceField(choices=ENTRY_STATUS_CHOICES, default=ENTRY_STATUS_NEW)
    contributors = EntryContributorSerializer(read_only=True, source="entry_to_user", many=True)
    files = FileSerializer(read_only=True, many=True)
    is_contributor = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = (
            "obj_type",
            "permissions",
            "id",
            "url",
            "title",
            "competition",
            "status",
            "crew_msg",
            "screen_msg",
            "vote_msg",
            "comment",
            "contributors",
            "files",
            "is_contributor",
            "is_owner",
            "owner",
            "order",
            "score",
        )

    def update(self, instance, validated_data):
        # stop update if compo is locked down
        if instance.competition.is_locked:
            raise ValidationError(
                {"error": "This competition is currently locked down pending stage show, and no edits are permitted."}
            )

        info = model_meta.get_field_info(instance)

        for attr, value in validated_data.items():
            if attr == "user_to_entry":
                print(value)
            elif attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)

        instance.save()

        return instance

    def create(self, validated_data):
        instance = super(EntrySerializer, self).create(validated_data)

        Contributor.objects.create(entry_id=instance.pk, user_id=self.context["request"].user.pk, is_owner=True)

        return instance

    def get_is_contributor(self, obj) -> bool:
        if not self.context["request"].user.is_authenticated:
            return False

        if obj in self.context["request"].user.entries.all():
            return True

        return False

    def get_is_owner(self, obj) -> bool:
        # make sure we are authenticated
        if not self.context["request"].user.is_authenticated:
            return False

        # fetch owner and make sure there is one
        owner = self.get_owner(obj)
        if not owner:
            return False

        # finally check if we are the owner
        return self.context["request"].user.pk == owner["uuid"]

    @extend_schema_field(NestedUserSerializer)  # TODO: maybe redo this method to return the same schema in all cases?
    def get_owner(self, obj):
        try:
            contributor = Contributor.objects.get(is_owner=True, entry_id=obj.pk)
        except Contributor.DoesNotExist:
            return None

        if self.context["request"] and self.context["request"].user.has_perm("competitions.view_entry_crewmsg"):
            return NestedUserWithDetailsSerializer(instance=contributor.user).data
        else:
            return NestedUserSerializer(instance=contributor.user).data


class EntryVoteSerializer(ValidatedModelSerializer):
    owner = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        read_only_fields = ("id", "title", "owner", "files")
        fields = (*read_only_fields,)

    def get_owner(self, obj) -> str:
        contrib = Contributor.objects.get(entry=obj, is_owner=True)
        return contrib.user.display_name

    def get_files(self, obj):
        request = self.context.get("request")
        qs = File.objects.filter(entry=obj, active=True)
        return NestedFileVoteSerializer(many=True, instance=qs, context={"request": request}).data


#
# Contributors
#


class ContributorSerializer(ValidatedModelSerializer):
    class Meta:
        model = Contributor
        fields = (
            "obj_type",
            "permissions",
            "id",
            "entry",
            "user",
            "extra_info",
            "is_owner",
        )

    def create(self, validated_data):
        try:
            owner = Contributor.objects.get(is_owner=True, entry_id=validated_data["entry"].id)
        except Contributor.DoesNotExist:
            raise serializers.ValidationError("Unable to add contributor as there is no owner of this entry")

        if not owner.user.id == self.context["request"].user.pk:
            raise serializers.ValidationError("Only the owner of an entry can add contributors")

        # stop creation if compo is locked down
        entry = Entry.objects.get(id=validated_data["entry"].id)
        if entry.competition.is_locked:
            raise ValidationError(
                {"error": "This competition is currently locked down pending stage show, and no edits are permitted."}
            )

        return super(ContributorSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        # stop update if compo is locked down
        if instance.entry.competition.is_locked:
            raise ValidationError(
                {"error": "This competition is currently locked down pending stage show, and no edits are permitted."}
            )

        return super(ContributorSerializer, self).update(instance, validated_data)


#
# Voting
#


class VoteSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="competitions-api:vote-detail")

    class Meta:
        model = Vote
        read_only_fields = ("obj_type", "url", "id", "user")
        fields = (*read_only_fields, "entry", "score")

    def validate(self, data):
        request = self.context.get("request")
        data["user"] = request.user

        return super(VoteSerializer, self).validate(data)

    def save(self, **kwargs):
        request = self.context.get("request")
        kwargs["user"] = request.user

        instance = super(VoteSerializer, self).save(**kwargs)

        return instance


#
# Results
#


class ResultsEntrySerializer(WritableNestedSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        read_only_fields = ("title", "owner", "score")
        fields = (*read_only_fields,)

    def get_owner(self, obj) -> str:
        contrib = Contributor.objects.get(entry=obj, is_owner=True)
        name = contrib.user.display_name

        # remove uuid from display name of users with default nick from
        # new-style GE which are also still using "aka" style display name
        return re.sub(
            r"\saka\.\s[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{6}",
            "",
            name,
        )


class ResultsSerializer(ValidatedModelSerializer):
    entries = ResultsEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Competition
        read_only_fields = ("name", "entries_count", "entries")
        fields = (*read_only_fields,)
