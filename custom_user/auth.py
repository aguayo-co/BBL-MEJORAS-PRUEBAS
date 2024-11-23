"""Define a Backend for settings based super user credentials."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()  # pylint: disable=invalid-name


class SettingsBackend:
    """
    Authenticate against the settings ADMIN_USER and ADMIN_PASSWORD.

    For example:

    ```
    ADMIN_USER=admin
    ADMIN_PASSWORD=pbkdf2_sha256$150000$Y15PGEeAaJWr$TGGdmzH71+q83Xrw1FH3VABDAnEFAAqpuTK+SOvpYYk=

    # When DEBUG is True, this is also valid:
    ADMIN_USER=admin
    ADMIN_PASSWORD=password
    ```
    """

    @staticmethod
    def authenticate(request, username=None, password=None):
        """
        Check credentials from settings and return the user.

        If a user with the given username does not exist, create one.
        """
        if not settings.ADMIN_USER or not settings.ADMIN_PASSWORD:
            return None

        login_valid = settings.ADMIN_USER == username

        pwd_valid = check_password(password, settings.ADMIN_PASSWORD)

        if settings.DEBUG and not pwd_valid:
            pwd_valid = password == settings.ADMIN_PASSWORD

        if not login_valid or not pwd_valid:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Create a new user. There's no need to set a password
            # because only the password from settings.py is checked.
            user = User.objects.create_superuser(
                username=username, email=None, password=None
            )
        return user

    @staticmethod
    def get_user(user_id):
        """Return the user for the given ID, or None if does not exist."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
