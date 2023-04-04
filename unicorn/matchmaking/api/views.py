from competitions.models import Competition
from django.db.models import Q
from matchmaking.models import MatchRequest
from rest_framework import generics
from rest_framework.response import Response
from utilities.api import ModelViewSet

from . import serializers


#
# Match Requests
#
class MatchRequestViewSet(ModelViewSet):
    queryset = MatchRequest.objects.all()
    serializer_class = serializers.MatchRequestSerializer


#
# Match Request Recommendations
#
class RecommendedListView(generics.ListAPIView):
    serializer_class = serializers.MatchRequestSerializer
    queryset = MatchRequest.objects.all()

    def list(self, request, *args, **kwargs):
        """Find MatchRequests from other users matching our active requests. To be a match, the other request must be
        (1) in a Competition we have a request in and which we do not currently participate in,
        (2) currently active and not authored by ourselves,
        (3) looking for the opposite as we do in that competition (Group vs. Player) and
        (4) within +/- 1 rank of our own"""

        # play nice and fetch the QuerySet like normal functions
        qs = self.get_queryset()

        # get competitions where user have active MRs and is not a contributor themselves
        competitions = Competition.objects.filter(matchrequests__author=request.user).filter(
            ~Q(entries__contributors=request.user)
        )

        # filter MRs to only find active ones from other users matching competitions above
        qs = qs.filter(active=True).filter(~Q(author=request.user)).filter(competition__in=competitions)

        # exclude all MRs with same looking_for and rank +/- 1
        for mr in MatchRequest.objects.filter(author=request.user).filter(active=True):
            qs = qs.exclude(looking_for=mr.looking_for).exclude(rank__lt=mr.rank - 1).exclude(rank__gt=mr.rank + 1)

        # pass QuerySet to serializer and return data to client
        serializer = serializers.MatchRequestSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)
