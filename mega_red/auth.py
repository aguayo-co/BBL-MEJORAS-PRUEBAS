"""Define a Backend for settings based super user credentials."""
import json
from hashlib import sha1
from socket import timeout
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from constance import config
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class MegaRedBackend:
    """
    Authenticate against MegaRed.
    """

    @staticmethod
    def authenticate(request, username=None, password=None, country=None):
        """
        Check credentials from settings and return the user.

        If a user with the given username does not exist, create one.
        """

        if not (username and password and country):
            return None

        params = urlencode(
            {
                "n_documento": username,
                "n_clave": password,
                "pais": country.dian_code,
                "key": sha1(
                    f"{country.dian_code}{username}".encode("utf-8")
                ).hexdigest(),
            }
        )
        megared_url = f"{config.MEGARED_AUTH_URL}?{params}"

        try:
            with urlopen(megared_url, timeout=15) as auth_request:
                mega_red_response = auth_request.read()
        except URLError:
            raise ValidationError(
                _(
                    "Tenemos un problema con nuestro sistema de autenticación."
                    " Por favor intenta más tarde o escríbenos en a cst@biblored.gov.co"
                )
            )
        except timeout:
            raise ValidationError(
                _(
                    "Tenemos un problema con nuestro sistema de autenticación."
                    " Por favor intenta nuevamente."
                )
            )

        try:
            mega_red_user = json.loads(mega_red_response)
        except json.decoder.JSONDecodeError:
            return None

        if not isinstance(mega_red_user, dict):
            return None

        email = mega_red_user.get("Correo", "") or ""
        name = mega_red_user.get("Nombre", "") or ""

        if not (isinstance(name, str) and isinstance(email, str)):
            raise ValidationError(
                _(
                    "Tus credenciales son válidas pero parece que hay un problema"
                    " con tu cuenta y no podemos autenticarte."
                    " Escríbenos a cst@biblored.gov.co"
                )
            )

        # Limit first name to our max_length.
        name = name.strip()[: User._meta.get_field("first_name").max_length]
        email = email.strip()

        try:
            validate_email(email)
        except ValidationError:
            email = ""

        # In Django, the username is a combination of the document and the country.
        # This is the unique ID in MegaRed.
        django_username = f"[MR][D:{username}][C:{country.dian_code}]"

        try:
            user = User.objects.get(username=django_username)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=django_username, email=email, first_name=name, country=country
            )
            review_permissions = Permission.objects.filter(codename__iendswith="review")
            for permission in review_permissions:
                user.user_permissions.add(permission)
        else:
            user.email = email
            user.first_name = name
            user.country = country
            user.save()

        return user

    @staticmethod
    def get_user(user_id):
        """Return the user for the given ID, or None if does not exist."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
