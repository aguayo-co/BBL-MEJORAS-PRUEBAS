"""Define Models for custom_user app."""

import re

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields.array import ArrayField
from django.contrib.postgres.search import TrigramDistance
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail.search import index
from wagtailmodelchooser import register_model_chooser

from mega_red.models import Country
from resources.models import ValidateFileMixin
from resources.validators import FileSizeValidator

from .managers import UserManager


@register_model_chooser
class User(index.Indexed, AbstractUser):
    """Define User model for CustomUser app."""

    __invitations = None
    __requests = None
    __invitations_count = None
    __requests_count = None
    __shared_resources_count = None

    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("país")
    )

    is_staff = models.BooleanField(verbose_name=_("es autorizado"), default=False)

    objects = UserManager(select_related=["profile", "country"])

    search_fields = [
        index.FilterField("id"),
        index.SearchField("username", partial_match=True),
        index.AutocompleteField("username"),
        index.SearchField("first_name", partial_match=True),
        index.AutocompleteField("first_name"),
        index.SearchField("last_name", partial_match=True),
        index.AutocompleteField("last_name"),
        index.SearchField("email", partial_match=True),
        index.AutocompleteField("email"),
    ]

    @property
    def full_name(self):
        """Return the full name for the user."""
        return (self.get_full_name() or "Usuario Sin Nombre").title()

    @property
    def initials(self):
        """Return initials for the user."""
        # Get words and no empty strings.
        words = list(filter(None, self.full_name.split(" ")))

        # No name?
        if not words:
            return "--"

        # We have at least one word
        first = words[0][0]

        # If the is no more than one word
        if len(words) == 1:
            return f"{first}{first}"

        return f"{first}{words[1][0]}"

    def get_absolute_url(self):
        """Return url for current instance."""
        return reverse("user-profile", args=[self.pk])

    @property
    def document(self):
        """Retorna el número único de documento de MegaRed."""
        try:
            return self.username.split("][")[1][2:]
        except IndexError:
            return None

    @property
    def is_megared(self):
        """Return True if user comes from MegaRed."""
        return self.username.startswith("[MR]")

    @property
    def requests_and_invitations(self):
        """Return the User's pending requests and invitations."""
        Collaborator = User.collaborator_set.field.model  # pylint: disable=invalid-name
        return Collaborator.objects.filter(
            (Q(collaborativecollection__owner=self) & Q(status=-2))
            | (Q(user=self) & Q(status=-1))
        )

    @property
    def invitations(self):
        """Return the User's pending invitations."""
        if self.__invitations is None:
            Collaborator = (
                User.collaborator_set.field.model
            )  # pylint: disable=invalid-name
            self.__invitations = Collaborator.objects.filter(
                Q(user=self) & Q(status=-1)
            )
        return self.__invitations

    @property
    def requests(self):
        """Return the User's pending requests."""
        if self.__requests is None:
            Collaborator = (
                User.collaborator_set.field.model
            )  # pylint: disable=invalid-name
            self.__requests = Collaborator.objects.filter(
                Q(collaborativecollection__owner=self) & Q(status=-2)
            )
        return self.__requests

    @property
    def invitations_count(self):
        if self.__invitations_count is None:
            self.__invitations_count = self.invitations.count()
        return self.__invitations_count

    @property
    def requests_count(self):
        if self.__requests_count is None:
            self.__requests_count = self.requests.count()
        return self.__requests_count

    @property
    def requests_and_invitations_count(self):
        """Return the User's pending requests and invitations quantity."""
        return self.invitations_count + self.requests_count

    @property
    def shared_resources_count(self):
        """Return user's shared resources notifications quantity."""
        if self.__shared_resources_count is None:
            self.__shared_resources_count = self.sharedresourceuser_set.filter(
                status=0
            ).count()
        return self.__shared_resources_count

    @property
    def notifications_count(self):
        """Return user's notifications quantity."""
        return self.shared_resources_count + self.requests_and_invitations_count

    def __str__(self):
        """
        Return a string representation for User.

        For MegaRed Users, returns document, country and fullname.
        For other users return username.
        """
        if self.is_megared:
            return f"{self.full_name} [{self.document}] [{self.country.dian_code}]"
        return super().__str__()

    @classmethod
    def search_users(cls, search_text, queryset=None):
        """Return search users db queryset."""
        if queryset is None:
            queryset = cls.objects.all()
        users = (
            queryset.annotate(
                complete_name=Concat("first_name", Value(" "), "last_name")
            )
            .annotate(distance=TrigramDistance("complete_name", search_text))
            .filter(profile__accept_terms=True)
            # Coincidencia superior al 60%
            .filter(Q(distance__lte=0.4) | Q(email__icontains=search_text))
            .order_by("distance")
        )
        return users

    @classmethod
    def get_user_extra_key(cls, user, extra_key_name, **kwargs):
        if extra_key_name == "shared_date" and "shared_resource" in kwargs:
            shared_date = None
            shared_resource = kwargs["shared_resource"]
            if shared_resource and shared_resource in user.sharedresource_set.all():
                shared_date_list = (
                    user.sharedresourceuser_set.filter(shared_resource=shared_resource)
                    .order_by("-created_at")
                    .values_list("created_at", flat=True)
                )
                shared_date = shared_date_list[0]
            return {"shared_date": shared_date}

    @classmethod
    def format_search_users_result_queryset(
        cls, users, search_text, extra_keys=None, **kwargs
    ):
        """Return search users db queryset results formatted."""
        if extra_keys is None:
            extra_keys = []
        response = {}
        for index, user in enumerate(users):
            response[index] = {
                "avatar": user.profile.avatar.url
                if hasattr(user, "profile") and user.profile.avatar
                else None,
                "name": user.full_name,
                "initials": user.initials,
                "id": user.id,
                "search_text": search_text,
            }
            for extra_key_name in extra_keys:
                response[index].update(
                    cls.get_user_extra_key(user, extra_key_name, **kwargs)
                )

        return response


class Profile(ValidateFileMixin, models.Model):
    """Store user profile fields."""

    SOCIAL_NETWORKS = {
        "facebook": ["Facebook", re.compile(r"https?://(?:www\.)?facebook\.com")],
        "twitter": ["Twitter", re.compile(r"https?://(?:www\.)?twitter\.com")],
        "instagram": ["Instagram", re.compile(r"https?://(?:www\.)?instagram\.com")],
        "youtube": ["YouTube", re.compile(r"https?://(?:www\.)?youtube\.com")],
    }

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, verbose_name=_("usuario")
    )
    avatar = models.ImageField(
        upload_to="users/avatar",
        null=True,
        blank=True,
        validators=[
            FileSizeValidator(1000000),
            FileExtensionValidator(["jpg", "jpeg", "png"]),
        ],
        verbose_name=_("imagen de perfil"),
    )
    biography = models.TextField(
        max_length=800, verbose_name=_("biografía"), null=True, blank=True
    )
    social_networks = ArrayField(
        base_field=models.URLField(blank=True),
        size=4,
        null=True,
        blank=True,
        verbose_name=_("redes sociales"),
    )
    accept_terms = models.BooleanField(
        verbose_name=_("acepta términos y condiciones"), default=False
    )

    @classmethod
    def get_social_networks_errors(cls, social_networks):
        """Validate social network profiles."""
        errors = {}

        for key, social_network in enumerate(cls.SOCIAL_NETWORKS):

            name = cls.SOCIAL_NETWORKS[social_network][0]
            regex = cls.SOCIAL_NETWORKS[social_network][1]
            value = social_networks[key] if len(social_networks) > key else None

            if value and not re.match(regex, value):
                errors[social_network] = ValidationError(
                    _("URL de perfil de %(social_network)s inválido."),
                    params={"social_network": name},
                )

        return errors

    def clean_fields(self, exclude=None):
        """Add validation for social network profiles."""
        super().clean_fields(exclude)

        if exclude is None:
            exclude = []

        if "social_networks" not in exclude:
            social_networks_errors = self.get_social_networks_errors(
                self.social_networks
            )
            if social_networks_errors:
                raise ValidationError(
                    {"social_networks": list(social_networks_errors.values())}
                )

    def get_absolute_url(self):
        """Return same URL as the parent user model."""
        return self.user.get_absolute_url()

    @property
    def social_networks_data(self):
        """Return Social Network data with names for each."""
        social_networks_data = {}
        for i, social_network in enumerate(self.SOCIAL_NETWORKS):
            url = None
            if self.social_networks and (i < len(self.social_networks)):
                url = self.social_networks[i]
            social_networks_data[social_network] = {
                "name": self.SOCIAL_NETWORKS[social_network][0],
                "url": url,
            }
        return social_networks_data
