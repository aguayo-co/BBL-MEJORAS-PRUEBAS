"""The Custom User App."""
from django.apps import AppConfig
from django.contrib.auth import user_logged_in, user_login_failed

from custom_user.signal_handlers import log_user_logged_in, log_user_login_failed


class CustomUserConfig(AppConfig):
    """The Custom User App Config."""

    name = "custom_user"
    verbose_name = "Gestión de usuarios personalizada"

    def ready(self):
        """Connect the App's Signals."""
        super().ready()
        user_logged_in.connect(log_user_logged_in)
        user_login_failed.connect(log_user_login_failed)
