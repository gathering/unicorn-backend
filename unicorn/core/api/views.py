from rest_framework_guardian.filters import ObjectPermissionsFilter
from utilities.api import ModelViewSet
from utilities.permissions import StandardObjectPermissions

from ..models import Event
from .serializers import EventSerializer


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    permission_classes = (StandardObjectPermissions,)
    filter_backends = (ObjectPermissionsFilter,)
