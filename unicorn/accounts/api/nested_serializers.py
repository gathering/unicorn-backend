from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from utilities.api import WritableNestedSerializer

from ..models import User, UserCard


class NestedUserSerializer(WritableNestedSerializer):
    class Meta:
        model = User
        fields = ("obj_type", "uuid", "display_name")


class NestedUserWithDetailsSerializer(WritableNestedSerializer):
    class Meta:
        model = User
        fields = (
            "obj_type",
            "uuid",
            "display_name",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "row",
            "seat",
        )


class NestedUserCardSerializer(WritableNestedSerializer):
    user = NestedUserSerializer()

    class Meta:
        model = UserCard
        fields = ("obj_type", "user", "value")

    def to_internal_value(self, data):
        if data is None:
            return None
        try:
            return self.Meta.model.objects.get(value=str(data))
        except (TypeError, ValueError):
            raise ValidationError("Invalid format on usercard")
        except ObjectDoesNotExist:
            raise ValidationError("Usercard not found")
