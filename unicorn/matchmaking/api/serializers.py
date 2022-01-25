from accounts.api.nested_serializers import NestedUserSerializer
from competitions.api.nested_serializers import NestedCompetitionSerializer
from matchmaking.models import MatchRequest
from utilities.api import ValidatedModelSerializer


class MatchRequestSerializer(ValidatedModelSerializer):
    competition = NestedCompetitionSerializer()
    author = NestedUserSerializer()

    class Meta:
        model = MatchRequest
        read_only_fields = ("obj_type", "permissions", "id", "author")
        fields = (
            "active",
            "text",
            "rank",
            "role",
            "competition",
            "looking_for",
            *read_only_fields,
        )

    def validate(self, data):
        """Specifically set the author to be the user submitting the request before running parent validation logic"""
        request = self.context.get("request")
        data["user"] = request.user

        return super(MatchRequestSerializer, self).validate(data)

    def save(self, **kwargs):
        """Specifically set the author to be the user submitting the request before saving"""
        request = self.context.get("request")
        kwargs["user"] = request.user

        instance = super(MatchRequestSerializer, self).save(**kwargs)

        return instance
