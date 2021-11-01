from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import serializers
from rest_framework.metadata import SimpleMetadata
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.utils.field_mapping import ClassLookupDict

#
# Renderers
#


class FormlessBrowsableAPIRenderer(BrowsableAPIRenderer):
    """
    Override the built-in BrowsableAPIRenderer to disable HTML forms.
    """

    def show_form_for_method(self, *args, **kwargs):
        return False

    def get_filter_form(self, data, view, request):
        return None


#
# Pagination
#


class OptionalLimitOffsetPagination(LimitOffsetPagination):
    """
    Override the stock paginator to allow setting limit=0 to disable pagination for a request. This returns all objects
    matching a query, but retains the same format as a paginated request. The limit can only be disabled if
    MAX_PAGE_SIZE has been set to 0 or None.
    """

    def paginate_queryset(self, queryset, request, view=None):

        try:
            self.count = queryset.count()
        except (AttributeError, TypeError):
            self.count = len(queryset)
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        self.request = request

        if self.limit and self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return list()

        if self.limit:
            return list(queryset[self.offset : self.offset + self.limit])
        else:
            return list(queryset[self.offset :])

    def get_limit(self, request):

        from django.conf import settings

        if self.limit_query_param:
            try:
                limit = int(request.query_params[self.limit_query_param])
                if limit < 0:
                    raise ValueError()
                # Enforce maximum page size, if defined
                if settings.MAX_PAGE_SIZE:
                    if limit == 0:
                        return settings.MAX_PAGE_SIZE
                    else:
                        return min(limit, settings.MAX_PAGE_SIZE)
                return limit
            except (KeyError, ValueError):
                pass

        return self.default_limit


#
# API Metadata
#


class OAuthTokenAuthenticationSchema(OpenApiAuthenticationExtension):
    target_class = "oauth2_provider.contrib.rest_framework.OAuth2Authentication"
    name = "tokenAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
        }


class ExtendedMetadata(SimpleMetadata):
    label_lookup = ClassLookupDict(
        {
            serializers.Field: "field",
            serializers.BooleanField: "boolean",
            serializers.NullBooleanField: "boolean",
            serializers.CharField: "string",
            serializers.UUIDField: "string",
            serializers.URLField: "url",
            serializers.EmailField: "email",
            serializers.RegexField: "regex",
            serializers.SlugField: "slug",
            serializers.IntegerField: "integer",
            serializers.FloatField: "float",
            serializers.DecimalField: "decimal",
            serializers.DateField: "date",
            serializers.DateTimeField: "datetime",
            serializers.TimeField: "time",
            serializers.ChoiceField: "choice",
            serializers.MultipleChoiceField: "multiple choice",
            serializers.FileField: "file upload",
            serializers.ImageField: "image upload",
            serializers.ListField: "list",
            serializers.DictField: "nested object",
            serializers.Serializer: "nested object",
            serializers.JSONField: "json",
        }
    )
