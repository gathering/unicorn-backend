import django_filters
from django.db.models import CharField, Q, Value
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _

from .models import User, UserCard


class UserSearchFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="search", label=_("Search"))
    usercard = django_filters.CharFilter(method="search_card", label=_("Usercard"))

    class Meta:
        model = User
        fields = ["username"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset.none()

        if len(value) < 4:
            return queryset.none()

        return (
            queryset.annotate(full_name=Concat("first_name", Value(" "), "last_name", output_field=CharField()))
            .filter(
                Q(username__icontains=value)
                | Q(email__iexact=value)
                | Q(first_name__icontains=value)
                | Q(last_name__icontains=value)
                | Q(full_name__iexact=value)
            )
            .distinct()
        )

    def search_card(self, queryset, name, value):
        if not value.strip():
            return queryset.none()

        try:
            card = UserCard.objects.get(value__iexact=value)
        except UserCard.DoesNotExist:
            return queryset.none()

        if not isinstance(card, UserCard):
            return queryset.none()

        return queryset.filter(pk=card.user.id)
