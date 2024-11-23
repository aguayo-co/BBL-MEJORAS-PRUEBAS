"""Define forms for the custom_user app."""

from django.forms import CharField, ModelForm, URLField, ValidationError
from django.forms.widgets import HiddenInput
from django.utils.translation import gettext_lazy as _

from resources.helpers import base64_file

from .models import Profile


class ProfileForm(ModelForm):
    """Define a Profile Form that handles social networks as separate fields."""

    cropped_image = CharField(required=False)

    class Meta:
        """Define Meta options for the Profile Form."""

        model = Profile
        fields = ["avatar", "biography", "social_networks", "accept_terms"]
        # Do not exclude to ensure validation is run properly
        # and values from cleaned_data are set on the instance.
        # Set as hidden instead.
        widgets = {"social_networks": HiddenInput()}

    def __init__(self, *args, **kwargs):
        """Create fields for each social network."""
        super().__init__(*args, **kwargs)
        social_networks = self.instance.social_networks or []
        for key, social_network in enumerate(Profile.SOCIAL_NETWORKS):
            value = social_networks[key] if len(social_networks) > key else None
            self.fields[social_network] = URLField(
                initial=value,
                required=False,
                widget=URLField.widget(
                    attrs={
                        "placeholder": _("Ingresa la URL de tu %(social_network)s")
                        % {"social_network": Profile.SOCIAL_NETWORKS[social_network][0]}
                    }
                ),
            )
        self.fields["accept_terms"].required = True

        if self.instance.accept_terms:
            self.fields.pop("accept_terms")

    def clean_avatar(self):
        """Convert cropped_image to file and assign it to avatar field."""
        if "cropped_image" in self.changed_data:
            cropped_image = base64_file(self.data.get("cropped_image"))
            return cropped_image
        return self.cleaned_data["avatar"]

    def clean(self):
        """
        Add validation for social networks and update its cleaned_data.

        Model will validate social networks but will put errors in the
        social_networks field and not on each individual field.
        This validation sets errors on the proper social network field.
        """
        cleaned_data = super().clean()

        social_networks = []
        for social_network in Profile.SOCIAL_NETWORKS:
            social_networks.append(cleaned_data.get(social_network, ""))

        social_networks_errors = self.instance.get_social_networks_errors(
            social_networks
        )
        if social_networks_errors:
            raise ValidationError(social_networks_errors)

        cleaned_data["social_networks"] = social_networks

        return cleaned_data
