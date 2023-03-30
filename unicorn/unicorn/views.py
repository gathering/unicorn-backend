from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class APIRootView(APIView):
    _ignore_model_permissions = True
    exclude_from_schema = True

    def get_view_name(self):
        return "API Root"

    def get(self, request, format=None):
        # List all applications available for everyone, including anonymous users
        data = {
            "competitions": reverse("competitions-api:api-root", request=request, format=format),
            "core": reverse("core-api:api-root", request=request, format=format),
            "matchmaking": reverse("matchmaking-api:api-root", request=request, format=format),
        }

        # Now let's add those only available for logged in users
        if self.request.user.is_authenticated:
            data["accounts"] = reverse("accounts-api:api-root", request=request, format=format)

        # Then we could add additional checks for applications which require special permissions

        # the end
        return Response(data)


class APIHealthView(APIView):
    _ignore_model_permissions = True

    def get_view_name(self):
        return "Health"

    def get(self, request, format=None):
        return Response("ok")
