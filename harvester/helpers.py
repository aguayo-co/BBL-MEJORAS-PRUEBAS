"""Define functions that can be used in multiple parts of the app."""

import datetime
import logging

from django.apps import apps
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db.models import ExpressionWrapper, Exists, OuterRef, BooleanField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_q.models import Schedule

from harvester.models import (
    AdminNotification,
    ContentResource,
    CreatorEquivalenceRelation,
    DataSource,
    EquivalenceRelation,
    LanguageEquivalenceRelation,
    RightsEquivalenceRelation,
    Set,
    SubjectEquivalenceRelation,
    TimestampModel,
    TypeEquivalenceRelation,
    settings,
    SetAndResource,
)
from resources.helpers import unparallel

bbl_logger = logging.getLogger("biblored")  # pylint: disable=invalid-name
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def schedule_delete_in_background_task(limit=1000, minutes=1):
    """Schedule the next deletion task."""
    func = "harvester.helpers.delete_in_background_task"
    Schedule.objects.update_or_create(
        name=func,
        next_run=(timezone.now() + datetime.timedelta(minutes=minutes)),
        defaults={
            "name": _("Borrado en Segundo Plano de Registros"),
            "kwargs": {"limit": limit},
            "func": func,
            "minutes": minutes,
            "schedule_type": "I",
        },
    )


@unparallel
def delete_in_background_task(limit=None):
    """Given queryset and limit, delete the elements in chunks."""
    total, __ = 0, {}
    if limit is None:
        limit = settings.DELETE_BACKGROUND_LIMIT

    models = apps.all_models["harvester"]
    for __, model in models.items():
        logger.debug(f"Borrando en segundo plano el modelo {model._meta.model_name}")
        marked = 0
        has_children = 0

        # Skip AdminNotification (Memory leak) TODO check rotation policy david.granados
        # Skip all intermediate models, must be deleted through Resource or Equivalence
        if issubclass(
            model,
            AdminNotification,
        ):
            logger.debug(f"Omitiendo modelo {model._meta.model_name}")
            continue

        if issubclass(model, Set):
            for a_set in model.objects.filter(to_delete=True).iterator():
                children = ContentResource.objects.filter(
                    setandresource__set=a_set, to_delete=False
                )
                marked += children.update(to_delete=True)
                has_children += marked

        if issubclass(model, DataSource):
            for data_source in model.objects.filter(to_delete=True).iterator():
                children = ContentResource.objects.filter(
                    data_source=data_source, to_delete=False
                )
                marked += children.update(to_delete=True)
                has_children += marked

        if issubclass(model, ContentResource):
            # Marcar todos los recursos que ya no están asociados a un set
            marked += (
                ContentResource.objects.alias(
                    associated_resource=ExpressionWrapper(
                        Exists(
                            SetAndResource.objects.filter(
                                resource=OuterRef("id"),
                            )
                        ),
                        output_field=BooleanField(),
                    ),
                )
                .filter(associated_resource=False, to_delete=False)
                .update(to_delete=True)
            )

            for resource in model.objects.filter(to_delete=True)[:limit].iterator():
                for equivalence_relation in [
                    LanguageEquivalenceRelation,
                    TypeEquivalenceRelation,
                    RightsEquivalenceRelation,
                    CreatorEquivalenceRelation,
                    SubjectEquivalenceRelation,
                ]:
                    children = equivalence_relation.objects.filter(
                        contentresource=resource, to_delete=False
                    )
                    marked += children.update(to_delete=True)
                    has_children += marked

        if marked:
            logger.debug(f"Marcados {marked} Recursos para eliminar.")
            return _(
                f"Marcados {marked} Recursos para eliminar en las"
                "próximas tareas de borrado en segundo plano."
            )

        if (
            issubclass(model, (TimestampModel, EquivalenceRelation))
            and not has_children
        ):
            sub_total, sub_objects = model.objects.filter(
                pk__in=model.objects.filter(to_delete=True)[:limit]
            ).delete()
            total += sub_total
            if total:
                logger.debug(
                    _(
                        f"Eliminados {total} elementos en segundo plano.",
                    )
                )
                return _(f"Eliminados {total} elementos en segundo plano.")
    return _(f"No se han encontrado elementos para eliminar.")


def send_mass_html_mail(
    datatuple,
    fail_silently=False,
    auth_user=None,
    auth_password=None,
    connection=None,  # pylint: disable=bad-continuation
):
    """Send mass mail with html body.

    Given a datatuple of (subject, message, html, from_email, recipient_list), send
    each message to each recipient list. Return the number of emails sent.

    If from_email is None, use the DEFAULT_FROM_EMAIL setting.
    If auth_user and auth_password are set, use them to log in.
    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.

    """
    connection = connection or get_connection(
        username=auth_user, password=auth_password, fail_silently=fail_silently
    )
    messages = []
    for subject, message, html, sender, recipient in datatuple:
        message = EmailMultiAlternatives(subject, message, sender, recipient)
        message.attach_alternative(html, "text/html")
        messages.append(message)
    return connection.send_messages(messages)


def set_dynamic_identifier_expired_task(data_source):
    """Given datasource, set all related resources identifier as expired."""
    resources = data_source.contentresource_set.update(dynamic_identifier_expired=True)
    return (
        "Expirados Identificadores Dinamicos de %(count)d %(items)s en segundo plano."
        % {
            "count": resources,
            "items": "recursos de contenido",
        }
    )
