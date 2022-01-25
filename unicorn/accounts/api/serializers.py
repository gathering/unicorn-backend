from rest_framework import serializers
from utilities.api import ChoiceField, ValidatedModelSerializer

from ..constants import USER_DISPLAY_CHOICES, USER_ROLE_CHOICES
from ..models import User


class UserSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="accounts-api:user-detail")
    role = ChoiceField(choices=USER_ROLE_CHOICES)
    display_name_format = ChoiceField(choices=USER_DISPLAY_CHOICES)

    class Meta:
        model = User
        read_only_fields = (
            "url",
            "accepted_location",
            "row",
            "seat",
            "crew",
            "display_name",
            "email",
            "role",
        )
        fields = (
            "obj_type",
            "permissions",
            "uuid",
            "display_name_format",
            "username",
            *read_only_fields,
        )
