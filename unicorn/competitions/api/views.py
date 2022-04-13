import os
import shutil
from zipfile import ZipFile

from competitions import filters
from competitions.models import Competition, Contributor, Entry, File, Genre, Vote
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from utilities.api import FieldChoicesViewSet, ModelViewSet

from unicorn.api import MethodNotAllowed, PassthroughRenderer, ServerError

from ..constants import ENTRY_STATUS_QUALIFIED, GENRE_CATEGORY_CREATIVE
from . import serializers

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
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={"error": "This Competition has entries and cannot be deleted!"},
            )

        return super(CompetitionViewSet, self).destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def push_to_toornament(self, request, pk=None):
        competition = self.get_object()
        competition.push_to_toornament()

        return Response({"status": "finished, check toornament to verify"})


class DownloadViewSet(ReadOnlyModelViewSet):
    queryset = Competition.objects.prefetch_related("entries")

    def list(self, *args):
        raise MethodNotAllowed()

    def retrieve(self, *args, **kwargs):
        raise MethodNotAllowed()

    @action(methods=["get"], detail=True, renderer_classes=(PassthroughRenderer,))
    def download(self, *args, **kwargs):
        compo = self.get_object()

        # check base path and create if it isn't there
        base_path = "/export"
        if not os.path.exists(base_path):
            try:
                os.mkdir(base_path)
            except OSError:
                raise ServerError("Unable to create base directory for export.")

        compo_name = "".join(char for char in compo.name if char.isalnum())
        compo_dir = base_path + "/" + compo_name
        if not os.path.exists(compo_dir):
            try:
                os.mkdir(compo_dir)
            except OSError:
                raise ServerError("Unable to create competition directory for export.")

        zip_path = compo_dir + "/" + compo_name + ".zip"
        zipObj = ZipFile(zip_path, "w")

        for entry in compo.entries.filter(status=ENTRY_STATUS_QUALIFIED):
            if not entry.files.filter(active=True).exists():
                continue

            # build some names
            title = "".join(
                char for char in entry.title if char.isalnum() or char == " "
            )
            owner_obj = Contributor.objects.get(entry=entry, is_owner=True)
            name = owner_obj.user.display_name
            owner = "".join(char for char in name if char.isalnum() or char == " ")

            # figure out which file to use
            f = entry.files.filter(active=True)
            if f.count() > 1:
                f = f.filter(type="main")

            # extract file ending
            f = f.first()
            ending = f.file.name[f.file.name.rfind(".") :]

            # build new path and copy file
            file_path = compo_dir + "/" + title + " by " + owner + ending
            file_path = file_path.replace(" ", "_")
            shutil.copy(f.file.path, file_path)
            zipObj.write(file_path, arcname=file_path.replace("/export", ""))

        zipObj.close()

        shutil.move(zip_path, f"/unicorn/unicorn/media/{compo_name}.zip")
        return HttpResponseRedirect(redirect_to=f"/media/{compo_name}.zip")


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
