import django_filters

#
# Filters
#


class NumericInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """
    Filters for a set of numeric values. Example: id__in=100,200,300
    """

    pass
