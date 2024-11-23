"""Signal Handlers/Receivers for Custom User App."""
import datetime
import logging

from constance import config
from django.contrib import messages
from django.contrib.auth import user_logged_in
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

bbl_logger = logging.getLogger("biblored")  # pylint: disable=invalid-name


def log_user_logged_in(sender, user, **kwargs):  # pylint: disable=unused-argument
    """Write to logs when a user has logged in."""
    bbl_logger.info(
        "El Usuario %(id)s (%(username)s) ha iniciado sesión",
        {"id": user.id, "username": user.username},
    )


def log_user_login_failed(
    sender, credentials, **kwargs
):  # pylint: disable=unused-argument
    """Write to logs when a user fails to log in."""
    bbl_logger.info(
        "Un usuario ha intentado iniciar sesión u:[%(username)s] c:[%(country)s]",
        {
            "country": credentials.get("country", ""),
            "username": credentials.get("username"),
        },
    )


@receiver(user_logged_in)
def admin_notifications(sender, request, user, **kwargs):
    today = datetime.date.today().weekday()
    notifications_days = [
        int(day) for day in config.ADMIN_NOTIFICATIONS_MESSAGE_DAYS.split(",")
    ]
    if user.is_staff and today in notifications_days:
        from harvester.models import AdminNotification

        notifications_qty = AdminNotification.objects.filter(
            created_at__gt=datetime.datetime.now() - datetime.timedelta(days=7)
        ).count()
        messages.add_message(
            request,
            messages.INFO,
            _(
                f"Hola {user.username} en los últimos 7 días se han publicado "
                f"{notifications_qty} contenidos."
            ),
        )
