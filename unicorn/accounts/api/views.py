from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework_guardian.filters import DjangoObjectPermissionsFilter
from utilities.api import FieldChoicesViewSet, ModelViewSet
from utilities.permissions import IsAuthenticatedAndNotAnon, StandardObjectPermissions

from ..constants import USER_ROLE_ANON
from ..filters import UserSearchFilter
from ..models import User
from .nested_serializers import NestedUserSerializer
from .serializers import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.exclude(role=USER_ROLE_ANON)
    serializer_class = UserSerializer

    permission_classes = (StandardObjectPermissions,)
    filter_backends = (DjangoObjectPermissionsFilter,)

    @action(detail=False, methods=["get"], url_path="@me")
    def get_self(self, request):
        try:
            qs = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(qs.get(pk=request.user.pk))
        except User.DoesNotExist:
            return Response(status=401)

        return Response(serializer.data)


class UserFieldChoicesViewSet(FieldChoicesViewSet):
    fields = ((User, ["display_name_format"]), (User, ["role"]), (User, ["gender"]))


class SearchView(ListAPIView):
    serializer_class = NestedUserSerializer
    filterset_class = UserSearchFilter

    permission_classes = (IsAuthenticatedAndNotAnon,)
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        if not self.request.query_params.get(
            "q", None
        ) and not self.request.query_params.get("usercard", None):
            return User.objects.none()

        return User.objects.exclude(role=USER_ROLE_ANON)


class MyGlobalPermissionsView(APIView):
    

    def get(self, request):
        """
        Return a list of all global permissions for the current user
        """
        user_perms = request.user.get_all_permissions()
        anon_perms = User.get_anonymous().get_all_permissions()
        perms = set.union(user_perms, anon_perms)

        return Response(sorted(perms))
