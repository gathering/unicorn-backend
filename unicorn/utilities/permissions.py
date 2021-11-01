from accounts.constants import USER_DISPLAY_AKA, USER_ROLE_ANON
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import Http404
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import get_objects_for_user
from rest_framework import permissions
from rest_framework.filters import BaseFilterBackend

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


def get_anonymous_user_instance(user_class):
    return user_class(
        uuid="c3961009-045c-43bd-a4d6-329209accddf",
        role=USER_ROLE_ANON,
        username="Anonymous",
        display_name_format=USER_DISPLAY_AKA,
    )


class StandardObjectPermissions(permissions.DjangoObjectPermissions):
    """
    Similar to 'DjangoObjectPermissions', but adding 'view' permissions.
    """

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

    authenticated_users_only = False

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, "_ignore_model_permissions", False):
            return True

        if not request.user or (
            not request.user.is_authenticated and self.authenticated_users_only
        ):
            return False

        if request.method in SAFE_METHODS:
            return True

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)
        anon = get_user_model().get_anonymous()

        user_has_access = request.user.has_perms(perms)
        anon_has_access = anon.has_perms(perms)

        if not user_has_access and not anon_has_access:
            user_count = get_objects_for_user(request.user, perms).count()
            if user_count > 0:
                return True

            anon_count = get_objects_for_user(anon, perms).count()
            if anon_count > 0:
                return True

        return user_has_access or anon_has_access

    def has_object_permission(self, request, view, obj):
        # authentication checks have already executed via has_permission
        queryset = self._queryset(view)
        model_cls = queryset.model
        user = request.user
        anon = get_user_model().get_anonymous()

        perms = self.get_required_object_permissions(request.method, model_cls)

        user_has_access = user.has_perms(perms, obj)
        anon_has_access = anon.has_perms(perms, obj)

        if not user_has_access and not anon_has_access:
            # If the user does not have permissions we need to determine if
            # they have read permissions to see 403, or not, and simply see
            # a 404 response.

            if request.method in SAFE_METHODS:
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise Http404

            read_perms = self.get_required_object_permissions("GET", model_cls)
            if not user.has_perms(read_perms, obj) and not anon.has_perms(
                read_perms, obj
            ):
                raise Http404

            # nope
            return False

        return True


class IsAuthenticatedAndNotAnon(permissions.BasePermission):
    """
    Allows access only to authenticated users (not anonymoususer).
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role is not USER_ROLE_ANON
        )


class PermissionRequiredMixinWithAnonymous(PermissionRequiredMixin):
    def check_permissions(self, request):
        forbidden = super(PermissionRequiredMixinWithAnonymous, self).check_permissions(
            request
        )
        if forbidden:
            perms = self.get_required_permissions(request)
            anon = get_user_model().get_anonymous()
            obj = self.get_permission_object()
            has_permissions = all(anon.has_perm(perm, obj) for perm in perms)
            if has_permissions:
                forbidden = None
        return forbidden


class DjangoObjectPermissionsFilter(BaseFilterBackend):
    """
    A filter backend that limits results to those where the requesting user
    has read object level permissions.
    """

    perm_format = "%(app_label)s.view_%(model_name)s"
    shortcut_kwargs = {"accept_global_perms": True}

    def __init__(self):
        assert "guardian" in settings.INSTALLED_APPS, (
            "Using DjangoObjectPermissionsFilter, "
            "but django-guardian is not installed."
        )

    def filter_queryset(self, request, queryset, view):
        # We want to defer this import until runtime, rather than import-time.
        # See https://github.com/encode/django-rest-framework/issues/4608
        # (Also see #1624 for why we need to make this import explicitly)
        from guardian.shortcuts import get_objects_for_user

        user = request.user
        anon = get_user_model().get_anonymous()

        permission = self.perm_format % {
            "app_label": queryset.model._meta.app_label,
            "model_name": queryset.model._meta.model_name,
        }

        user_objects = get_objects_for_user(
            user, permission, queryset, **self.shortcut_kwargs
        )
        anon_objects = get_objects_for_user(
            anon, permission, queryset, **self.shortcut_kwargs
        )

        objects = user_objects | anon_objects
        return objects.distinct()
