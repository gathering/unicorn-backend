from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm, remove_perm
from matchmaking.models import MatchRequest


@receiver(post_save, sender=MatchRequest)
def add_matchrequest_view_active(sender, instance, created, **kwargs):
    """Add permissions to allow anyone to view active MatchRequests"""
    g = Group.objects.get(name="p-anonymous")

    if instance.active:
        assign_perm("view_matchrequest", g, instance)
    else:
        remove_perm("view_matchrequest", g, instance)


@receiver(post_save, sender=MatchRequest)
def add_matchrequest_object_permissions(sender, instance, **kwargs):
    """Make sure we (the author) have enough permissions to our own MatchRequest"""
    assign_perm("view_matchrequest", instance.author, instance)
    assign_perm("change_matchrequest", instance.author, instance)
    assign_perm("delete_matchrequest", instance.author, instance)
