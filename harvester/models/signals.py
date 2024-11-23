"""Define signals for Harvester app."""
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from harvester.models import CollaborativeCollection, Collection, Review


@receiver(post_delete)
def delete_file_on_delete(
    sender, instance, **kwargs  # pylint: disable=bad-continuation
):  # pylint: disable=unused-argument
    """
    Delete a file after model deletion.

    The model may need the name of the object for its __str__, for that reason
    it is not possible to call `file_instance.delete()`.
    An error is caused inside Django admin if it access the `__str__`
    of the instance after being deleted.
    """
    for field in instance._meta.get_fields(include_parents=False):
        if isinstance(field, models.FileField):
            file_instance = getattr(instance, field.name)
            if file_instance.name:
                file_instance.storage.delete(file_instance.name)


@receiver(pre_save)
def delete_file_on_change(
    sender, instance, **kwargs  # pylint: disable=bad-continuation
):  # pylint: disable=unused-argument,bad-continuation
    """
    Delete old file if changed on model update.

    The model may need the name of the object for its `__str__`, for that reason
    it is not possible to call `file_instance.delete()`.
    It is possible that the `__str__` of the old instance is required after
    deleting the file.
    """
    if not instance.pk:
        return

    for field in instance._meta.get_fields():
        if isinstance(field, models.FileField):
            new_file = getattr(instance, field.name)

            try:
                old_instance = sender.objects.get(pk=instance.pk)
            except sender.DoesNotExist:
                return
            else:
                old_file = getattr(old_instance, field.name)

            if old_file == new_file:
                return

            if old_file.name:
                old_file.storage.delete(old_file.name)


def notify_admin(instance, created):
    if created and hasattr(instance, "admin_notification"):
        instance.admin_notification.create()


@receiver(post_save, sender=Review)
def review_created_admin_notification(sender, instance, created, **kwargs):
    notify_admin(instance, created)


@receiver(post_save, sender=Collection)
def collection_created_admin_notification(sender, instance, created, **kwargs):
    notify_admin(instance, created)


@receiver(post_save, sender=CollaborativeCollection)
def collaborative_collection_created_admin_notification(
    sender, instance, created, **kwargs
):
    notify_admin(instance, created)
