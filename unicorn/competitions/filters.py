import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from utilities.filters import NumericInFilter

from .constants import GENRE_CATEGORY_CHOICES
from .models import Competition, Entry, Genre


class GenreFilter(django_filters.FilterSet):
    id__in = NumericInFilter(field_name="id", lookup_expr="in")
    q = django_filters.CharFilter(method="search", label=_("Search"))

    class Meta:
        model = Genre
        fields = ["name"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(Q(name__icontains=value)).distinct()


class CompetitionFilter(django_filters.FilterSet):
    id__in = NumericInFilter(field_name="id", lookup_expr="in")
    q = django_filters.CharFilter(method="search", label=_("Search"))
    category = django_filters.MultipleChoiceFilter(
        field_name="genre__category",
        choices=GENRE_CATEGORY_CHOICES,
        null_value=None,
        label=_("Category"),
    )
    genre = django_filters.ModelMultipleChoiceFilter(field_name="genre", queryset=Genre.objects.all(), label=_("Genre"))
    name = django_filters.CharFilter()
    info = django_filters.CharFilter()
    rules = django_filters.CharFilter()
    published = django_filters.BooleanFilter()
    report_win_loss = django_filters.BooleanFilter()
    rsvp = django_filters.BooleanFilter()
    team_required = django_filters.BooleanFilter()

    register_time_start = django_filters.DateTimeFromToRangeFilter()
    register_time_end = django_filters.DateTimeFromToRangeFilter()
    run_time_start = django_filters.DateTimeFromToRangeFilter()
    run_time_end = django_filters.DateTimeFromToRangeFilter()
    vote_time_start = django_filters.DateTimeFromToRangeFilter()
    vote_time_end = django_filters.DateTimeFromToRangeFilter()
    show_time_start = django_filters.DateTimeFromToRangeFilter()
    show_time_end = django_filters.DateTimeFromToRangeFilter()

    has_entries = django_filters.BooleanFilter(method="_has_entries", label=_("Has Entries"))

    class Meta:
        model = Competition
        fields = ["name"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(Q(name__icontains=value) | Q(info__icontains=value) | Q(genre__name=value)).distinct()

    def _has_entries(self, queryset, name, value):
        return queryset.filter(Q(entries=bool(value) or None))


class EntryFilter(django_filters.FilterSet):
    id__in = NumericInFilter(field_name="id", lookup_expr="in")
    competition_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Competition.objects.all(), label="Competition ID"
    )
    name = django_filters.CharFilter()
    status = django_filters.NumberFilter()

    class Meta:
        model = Entry
        fields = ["name"]
