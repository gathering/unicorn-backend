from competitions import filters
from competitions.models import Competition, Contributor, Entry, File, Genre, Vote
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from utilities.api import FieldChoicesViewSet, ModelViewSet

from . import serializers
from ..constants import ENTRY_STATUS_QUALIFIED, GENRE_CATEGORY_CREATIVE

#
# Field choices
#


class CompetitionsFieldChoicesViewSet(FieldChoicesViewSet):
    fields = (
        (Genre, ["category"]),
        (Competition, ["state"]),
        (Entry, ["status"]),
        (File, ["status"]),
    )


#
# Genres
#


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer


#
# Competitions
#


class CompetitionViewSet(ModelViewSet):
    """
    list:
    Return a list of all competitions

    create:
    Create a new competition

    retrieve:
    Get a single competition

    update:
    Make changes to a competition

    partial_update:
    Make partial changes to a competition

    destroy:
    Delete a competition
    """

    queryset = Competition.objects.select_related("genre").prefetch_related("entries")
    serializer_class = serializers.CompetitionSerializer
    filterset_class = filters.CompetitionFilter

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.entries.count():
            return Response(status=status.HTTP_409_CONFLICT, data={"error": "This Competition has entries and cannot be deleted!"})

        return super(CompetitionViewSet, self).destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def push_to_toornament(self, request, pk=None):
        competition = self.get_object()
        competition.push_to_toornament()

        return Response({"status": "finished, check toornament to verify"})


#
# Entries
#


class EntryViewSet(ModelViewSet):
    filterset_class = filters.EntryFilter

    @action(detail=True, methods=["get"])
    def toornament_info(self, request, pk=None):
        entry = self.get_object()
        try:
            info = entry.toornament_info()
        except NotImplementedError as e:
            return Response({"error": str(e)}, status=400)
        except RuntimeError as e:
            return Response({"info": str(e)}, status=204)

        return Response(info)

    def get_queryset(self):
        if self.request:
            if self.request.query_params.get("vote", None):
                return Entry.objects.filter(status=ENTRY_STATUS_QUALIFIED)

        return Entry.objects.select_related("competition")

    def get_serializer_class(self):
        if self.request:
            if self.request.query_params.get("vote", None):
                return serializers.EntryVoteSerializer

        return serializers.EntrySerializer


class VoteViewSet(ModelViewSet):
    serializer_class = serializers.VoteSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Vote.objects.filter(user=self.request.user)
        else:
            return Vote.objects.none()


#
# Contributors
#
class ContributorViewSet(ModelViewSet):
    queryset = Contributor.objects.all()
    serializer_class = serializers.ContributorSerializer


#
# Results
#


class ResultsViewSet(ModelViewSet):
    queryset = (
        Competition.objects.filter(published=True)
        .filter(genre__category=GENRE_CATEGORY_CREATIVE)
        .order_by("genre", "name")
        .prefetch_related(
            Prefetch(
                "entries",
                queryset=Entry.objects.filter(status=ENTRY_STATUS_QUALIFIED).order_by(
                    "-score", "order"
                ),
            )
        )
    )
    serializer_class = serializers.ResultsSerializer
