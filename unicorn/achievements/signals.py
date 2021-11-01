from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm

from .models import Level


@receiver(post_save, sender=Level)
def level_assign_permissions(sender, instance, created, **kwargs):
    if created:
        # give permissions to the user itself
        assign_perm("view_level", instance.user, instance)
        assign_perm("change_level", instance.user, instance)

        # .. and users which need to award it
        g, c = Group.objects.get_or_create(name="achievement-award")
        assign_perm("view_level", g, instance)
        assign_perm("change_level", g, instance)
