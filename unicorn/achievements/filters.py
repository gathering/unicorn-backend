import django_filters
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from utilities.filters import NumericInFilter

from .constants import ACHIEVEMENT_TYPE_CHOICES
from .models import Achievement, Category, Level


class CategoryFilter(django_filters.FilterSet):
    id__in = NumericInFilter(field_name="id", lookup_expr="in")
    q = django_filters.CharFilter(method="search", label=_("Search"))

    class Meta:
        model = Category
        fields = ["name"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(Q(name__icontains=value)).distinct()


class LevelFilter(django_filters.FilterSet):
    id__in = NumericInFilter(field_name="id", lookup_expr="in")
    user = django_filters.NumberFilter()

    class Meta:
        model = Level
        fields = ["id"]


class AchievementFilter(django_filters.FilterSet):
    id__in = NumericInFilter(field_name="id", lookup_expr="in")
    q = django_filters.CharFilter(method="search", label=_("Search"))
    user = django_filters.UUIDFilter(method="by_user", label=_("By User"))

    category = django_filters.ModelMultipleChoiceFilter(
        field_name="category", queryset=Category.objects.all(), label=_("Category")
    )
    type = django_filters.MultipleChoiceFilter(
        choices=ACHIEVEMENT_TYPE_CHOICES, null_value=None, label=_("Type")
    )

    manual_validation = django_filters.BooleanFilter()
    multiple = django_filters.BooleanFilter()
    hidden = django_filters.BooleanFilter()

    class Meta:
        model = Achievement
        fields = ["name"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(requirement__icontains=value)
        ).distinct()

    def by_user(self, queryset, name, value):
        return queryset.filter(Q(users__uuid=value)).distinct()
