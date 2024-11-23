"""Define forms for MegaRed app."""

from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.forms import BooleanField, Form, ModelChoiceField
from django.utils.translation import gettext_lazy as _

from harvester.models import Collaborator

from .models import Country


class MegaRedAuthenticationForm(AuthenticationForm):
    """Extend Login form with Country and Remember option."""

    country = ModelChoiceField(
        label=_("Selecciona tu país"),
        empty_label=_("Selecciona tu país"),
        required=False,
        queryset=Country.objects.order_by("name").all(),
        to_field_name="dian_code",
    )
    remember = BooleanField(required=False, label=_("Recordarme"))
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": _(
            _("Tu documento, contraseña o país no son correctos, intenta nuevamente.")
        ),
    }

    def __init__(self, *args, **kwargs):
        """Alter form widget labels."""
        super().__init__(*args, **kwargs)

        self.fields["username"].label = _("Documento de identidad")
        self.fields["username"].widget.attrs["placeholder"] = _(
            "Ingresa tu número de identificación"
        )
        self.fields["password"].widget.attrs["placeholder"] = _("Ingresa tu contraseña")

        # Make field required in browser but add a countryless option.
        self.fields["country"].widget.attrs["required"] = True
        self.fields["country"].choices = [
            country for country in self.fields["country"].choices
        ]
        self.fields["country"].choices.insert(1, ("", _("- Sin país -")))

    def clean(self):
        """Add Country as credential, if one is received."""
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        country = self.cleaned_data.get("country")

        if username is not None and password:

            credentials = {"username": username, "password": password}
            if country:
                credentials["country"] = country

            self.user_cache = authenticate(self.request, **credentials)
            if self.user_cache is None:
                raise self.get_invalid_login_error()

            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class NotificationForm(Form):
    """Form to handle requests/invitations, this is a dummy form."""

    accept = ModelChoiceField(label=_("Aceptar"), queryset=None, required=False)
    reject = ModelChoiceField(label=_("Cancelar"), queryset=None, required=False)

    def __init__(self, user, *args, **kwargs):
        """Append querysets to fields."""
        super().__init__(*args, **kwargs)
        if user:
            self.user = user
            collaborators = user.requests_and_invitations
            self.fields["accept"].queryset = collaborators
            self.fields["reject"].queryset = collaborators

    def save(self):
        """Accept or delete a collaborator invitation or request."""
        collaborator = self.cleaned_data.get("accept", None) or self.cleaned_data.get(
            "reject", None
        )

        if self.cleaned_data["accept"]:
            collaborator.status = 1
            collaborator.save()

        if self.cleaned_data["reject"]:
            return Collaborator.objects.filter(pk=collaborator.pk).delete()


class InvitationsForm(NotificationForm):
    """Form to handle invitations, this is a dummy form."""

    def __init__(self, notifications, *args, **kwargs):
        """Append querysets to fields."""
        super().__init__(None, *args, **kwargs)
        self.fields["accept"].queryset = notifications
        self.fields["reject"].queryset = notifications


class RequestsForm(InvitationsForm):
    """Form to handle requests, this is a dummy form."""
