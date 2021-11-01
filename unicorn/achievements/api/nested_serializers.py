from rest_framework import serializers
from utilities.api import WritableNestedSerializer

from ..models import Category, Team

#
# Teams
#


class NestedTeamSerializer(WritableNestedSerializer):
    class Meta:
        model = Team
        fields = ("id", "name")


#
# Categories
#


class NestedCategorySerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="achievements-api:category-detail"
    )

    class Meta:
        model = Category
        fields = ("obj_type", "url", "id", "name")
