from django.contrib.auth.models import Group
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Student


@receiver(pre_save, sender=Student)
def unsync_program_with_groups(sender, instance, raw, **kwargs):
    if raw:
        return
    if not instance.pk:
        return
    s = Student.objects.select_related('program').get(pk=instance.pk)
    if s.program is None:
        return
    g, _ = Group.objects.get_or_create(name=s.program.name)
    instance.user.groups.remove(g)


@receiver(post_save, sender=Student)
def sync_program_with_groups(sender, instance, created, raw, **kwargs):
    if created or raw:
        return
    if instance.program is None:
        return
    g, _ = Group.objects.get_or_create(name=instance.program.name)
    instance.user.groups.add(g)
