from rest_framework import serializers
from utilities.api import ValidatedModelSerializer, WritableNestedSerializer

from ..models import Event


class EventSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="core-api:event-detail")

    class Meta:
        model = Event
        read_only_fields = ("id",)
        fields = (
            "url",
            *read_only_fields,
            "name",
            "location",
            "start_date",
            "end_date",
            "visible",
            "active",
        )


class NestedEventSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="core-api:event-detail")

    class Meta:
        model = Event
        read_only_fields = ("id",)
        fields = (
            "url",
            *read_only_fields,
            "name",
            "location",
        )
