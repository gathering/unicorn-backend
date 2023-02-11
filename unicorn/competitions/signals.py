from competitions.constants import (
    COMPETITION_VISIBILITY_CREW,
    COMPETITION_VISIBILITY_HIDDEN,
    COMPETITION_VISIBILITY_PUBLIC,
)
from competitions.models import Competition, Contributor, Entry, File, Vote
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm, remove_perm
from zoodo_utils.tus.signals import tus_upload_finished_signal
from zoodo_utils.tus.views import TusUpload


@receiver(post_save, sender=Competition)
def add_competition_view_published(sender, instance, created, **kwargs):
    anon = Group.objects.get(name="p-anonymous")
    crew = Group.objects.get(name="p-crew")

    # if visibility is set to hidden, we remove crew and anon permissions
    # regardless if the action is publish or unpublish
    if instance.visibility == COMPETITION_VISIBILITY_HIDDEN:
        remove_perm("view_competition", anon, instance)
        remove_perm("view_competition", crew, instance)

    elif instance.visibility == COMPETITION_VISIBILITY_CREW:
        # make sure to remove anon permissions
        remove_perm("view_competition", anon, instance)

        if instance.published:
            assign_perm("view_competition", crew, instance)
        else:
            remove_perm("view_competition", crew, instance)

    elif instance.visibility == COMPETITION_VISIBILITY_PUBLIC:
        # make sure to remove crew permissions, keeping things tidy
        remove_perm("view_competition", crew, instance)

        if instance.published:
            assign_perm("view_competition", anon, instance)
        else:
            remove_perm("view_competition", anon, instance)


@receiver(post_save, sender=Competition)
def assure_compoadmin_permissions(sender, instance, created, **kwargs):
    if created:
        try:
            group = Group.objects.get(name="p-compoadmin-{}".format(str(instance.genre.category)))
            assign_perm("view_competition", group, instance)
            assign_perm("change_competition", group, instance)
            assign_perm("delete_competition", group, instance)
        except Group.DoesNotExist:
            pass


@receiver(post_save, sender=Entry)
def assure_compoadmin_entry_permissions(sender, instance, created, **kwargs):
    if created:
        try:
            group = Group.objects.get(name="p-compoadmin-{}".format(str(instance.competition.genre.category)))
            assign_perm("view_entry", group, instance)
            assign_perm("change_entry", group, instance)
            assign_perm("delete_entry", group, instance)
        except Group.DoesNotExist:
            pass


@receiver(post_save, sender=Contributor)
def contributor_permissions(instance, created, **kwargs):
    # find all other contributors in our entry
    theothers = Contributor.objects.filter(entry=instance.entry)
    if instance.pk:
        theothers = theothers.exclude(pk=instance.pk)

    # remove our permissions towards other contributors if we are not the owner anymore
    if not instance.is_owner:
        for contrib in theothers:
            remove_perm("change_contributor", instance.user, contrib)
            remove_perm("delete_contributor", instance.user, contrib)

    # grant view permissions to all
    assign_perm("view_contributor", instance.user, instance)
    for contrib in theothers:
        assign_perm("view_contributor", contrib.user, instance)

    # grant modify permissions to ourselves
    assign_perm("change_contributor", instance.user, instance)
    assign_perm("delete_contributor", instance.user, instance)

    # grant modify permissions to the owner
    owner = Contributor.objects.get(entry=instance.entry, is_owner=True)
    assign_perm("change_contributor", owner.user, instance)
    assign_perm("delete_contributor", owner.user, instance)


@receiver(post_save, sender=Contributor)
def adjust_entry_permissions_for_contributor(sender, instance, created, **kwargs):
    # all contributors can see the entry
    assign_perm("view_entry", instance.user, instance.entry)

    # only owners can modify it
    if instance.is_owner:
        assign_perm("change_entry", instance.user, instance.entry)
        assign_perm("delete_entry", instance.user, instance.entry)

        # remove from all other contributors
        theothers = Contributor.objects.filter(entry=instance.entry)
        theothers = theothers.exclude(pk=instance.pk)
        for contrib in theothers:
            remove_perm("change_entry", contrib.user, instance.entry)
            remove_perm("delete_entry", contrib.user, instance.entry)

    # remove permissions for anyone else which might have these permissions
    else:
        remove_perm("change_entry", instance.user, instance.entry)
        remove_perm("delete_entry", instance.user, instance.entry)


@receiver(tus_upload_finished_signal, sender=TusUpload)
def register_file_upload(sender, **kwargs):
    data = {
        "name": kwargs["metadata"]["filename"],
        "type": kwargs["metadata"]["filetype"],
        "size": kwargs["file_size"],
        "hash": kwargs["filename"],
    }

    # create a file object and push in some basic data
    f = File()
    f.file.name = data["hash"]
    f.name = data["name"]
    f.mime = data["type"]

    # then add the info we need for association elsewhere
    f.type = kwargs.get("type")
    f.uploader_id = kwargs.get("uploader")
    f.entry = Entry.objects.get(pk=kwargs.get("entry_id"))

    f.clean()

    # and then of course let's save
    f.save()


@receiver(post_save, sender=Vote)
def add_vote_object_permissions(sender, instance, **kwargs):
    assign_perm("view_vote", instance.user, instance)
    assign_perm("change_vote", instance.user, instance)
    assign_perm("delete_vote", instance.user, instance)


@receiver(post_save, sender=Vote)
def recalculate_entry_score(sender, instance, **kwargs):
    instance.entry.update_score()
