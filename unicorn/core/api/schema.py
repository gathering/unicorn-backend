from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import build_basic_type, build_object_type
from drf_spectacular.types import OpenApiTypes


class ChoiceFieldFix(OpenApiSerializerFieldExtension):
    target_class = "utilities.api.ChoiceField"

    def map_serializer_field(self, auto_schema, direction):
        if direction == "request":
            return build_basic_type(OpenApiTypes.STR)

        elif direction == "response":
            return build_object_type(
                properties={
                    "value": build_basic_type(OpenApiTypes.STR),
                    "label": build_basic_type(OpenApiTypes.STR),
                }
            )
