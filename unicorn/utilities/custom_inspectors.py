from drf_yasg import openapi
from drf_yasg.inspectors import FieldInspector, FilterInspector, PaginatorInspector
from rest_framework.fields import ChoiceField


class NullableBooleanFieldInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):

        if (
            isinstance(result, openapi.Schema)
            and isinstance(obj, ChoiceField)
            and result.type == "boolean"
        ):
            keys = obj.choices.keys()
            if set(keys) == {None, True, False}:
                result["x-nullable"] = True
                result.type = "boolean"

        return result


class IdInFilterInspector(FilterInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        if isinstance(result, list):
            params = [
                p
                for p in result
                if isinstance(p, openapi.Parameter) and p.name == "id__in"
            ]
            for p in params:
                p.type = "string"

        return result


class NullablePaginatorInspector(PaginatorInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        if method_name == "get_paginated_response" and isinstance(
            result, openapi.Schema
        ):
            next = result.properties["next"]
            if isinstance(next, openapi.Schema):
                next["x-nullable"] = True
            previous = result.properties["previous"]
            if isinstance(previous, openapi.Schema):
                previous["x-nullable"] = True

        return result
