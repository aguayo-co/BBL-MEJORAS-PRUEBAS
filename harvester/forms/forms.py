"""Define Forms for harvester app."""

import datetime
import io

from django import forms
from django.contrib.admin import widgets
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.core.validators import FileExtensionValidator
from django.db.models import Q
from django.forms import BaseFormSet, ModelForm, ModelMultipleChoiceField
from django.template import loader
from django.utils.translation import gettext_lazy as _

from harvester.common import DUBLIN_CORE_DEFAULT_ASSOCIATION
from harvester.forms.fields import (
    CollectionsGroupsField,
    DataSourceConfigField,
    DynamicUrlField,
    CaptureExpressionField,
)
from resources.forms import FiltersForm
from resources.helpers import base64_file
from search_engine.functions.es_backend_helpers import mark_resource_for_reindex

from ..helpers import send_mass_html_mail
from ..models import (
    CollaborativeCollection,
    Collaborator,
    Collection,
    CollectionAndResource,
    CollectionsGroup,
    CollectionsGroupCollection,
    ContentResource,
    DataSource,
    DynamicIdentifierConfig,
    Review,
    Set,
    SharedResource,
    SharedResourceUser,
    User,
)
from .fields import EquivalenceMultipleChoiceField

ONLINE_RESOURCES_CHOICES = [
    # (None, _("todos")),
    (True, _("acceso digital")),
    # (False, _("ubicación física")),
]
COLLECTION_TYPE_CHOICES = (
    ("collaborative", _("Colección pública colaborativa")),
    ("public", _("Colección pública cerrada")),
    ("private", _("Colección privada")),
)


class FormNameMixin:
    """Parent for forms that share a single view."""

    form_name = forms.CharField(
        max_length=60, widget=forms.HiddenInput(), required=False
    )


class GetCollectionsGroupInitialMixin:
    @staticmethod
    def get_collections_groups_form_initial(
        collection, user_groups, collections_groups_initial=None
    ):
        if not collections_groups_initial and user_groups:
            if hasattr(collection, "groups_list"):
                collection_groups_set = set(collection.groups_list)
            else:
                real_object = collection
                if hasattr(collection, "content_object"):
                    real_object = collection.content_object
                collection_groups_set = set(
                    real_object.collections_groups.all().values_list(
                        "collections_group", flat=True
                    )
                )
            user_groups_set = set(user_groups)
            collections_groups_initial = list(
                user_groups_set.intersection(collection_groups_set)
            )

        initial = {
            "collections_groups": collections_groups_initial,
            "collections_groups_checkboxes": collections_groups_initial,
        }

        return initial


class DataSourceNameForm(forms.Form):
    """A form that contains a readonly str representation of a datasource."""

    data_source = forms.CharField(disabled=True, label=_("fuente de datos"))
    group_id = forms.CharField(widget=forms.HiddenInput(), required=True)

    def clean_group_id(self):
        """Validate group_id has not been modified."""
        group_id = self.cleaned_data["group_id"]
        if group_id != self.initial["group_id"]:
            raise forms.ValidationError(
                _(
                    "Parece que dos formularios han sido abiertos a la vez."
                    " Por favor no completes lo formularios en simultanea."
                )
            )
        return group_id


class UploadFileForm(DataSourceNameForm):
    """A form with a file field to upload allowed files."""

    ALLOWED_EXTENSIONS = ["csv", "txt", "tsv", "xml", "mrc"]
    file_field = forms.FileField(
        help_text=_(
            "Se permiten archivos codificados con UTF-8 con las siguientes extensiones:"
            " %(extensions)s."
        )
        % {"extensions": ", ".join(ALLOWED_EXTENSIONS)},
        label=_("archivo de recursos"),
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
    )

    def clean_file_field(self):
        """Ensure file is in UTF-8."""
        file_field = self.cleaned_data["file_field"]
        _file = io.TextIOWrapper(file_field, encoding="utf-8")
        try:
            _file.readlines()
        except UnicodeDecodeError:
            raise forms.ValidationError(
                _("Subiste un archivo que no está codificado con UTF-8.")
            )
        else:
            # https://bugs.python.org/issue21363
            _file.detach()
        file_field.seek(0)
        return file_field


class SelectSetsForm(DataSourceNameForm):
    """Form for selecting multiples sets with a search field."""

    sets = forms.MultipleChoiceField(
        widget=widgets.FilteredSelectMultiple(
            is_stacked=False, verbose_name=_("Sets a cosechar")
        ),
        label="",
    )

    class Media:
        """Define options for SelectSetsForm."""

        css = {"all": ("/static/admin/css/widgets.css",)}
        js = ("/admin/jsi18n",)


class MappingAbstractForm(DataSourceNameForm):
    """A Dummy class to add fields and inputs."""


class ConfirmHarvestForm(DataSourceNameForm):
    """The confirmation form, can be a preview in the future."""


class ContentResourceCollectionsForm(forms.Form):
    """Form to edit the Collections a Resource belongs to."""

    collections_select = forms.ModelMultipleChoiceField(
        label=_("Buscar"), queryset=None, required=False
    )
    collections = forms.ModelMultipleChoiceField(
        queryset=None, required=False, widget=forms.CheckboxSelectMultiple
    )
    collaborative_collections = forms.ModelMultipleChoiceField(
        queryset=None, required=False, widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, instance, user, *args, **kwargs):
        """Set queryset for collections field."""
        self.instance = instance

        super().__init__(*args, **kwargs)

        self.fields["collections_select"].queryset = Collection.objects.filter(
            owner=user
        )
        self.fields["collections_select"].initial = instance.collection_set.filter(
            owner=user
        )

        self.fields["collections"].queryset = Collection.objects.filter(
            owner=user
        ).exclude_subclasses()
        self.fields["collections"].initial = instance.collection_set.filter(
            owner=user
        ).exclude_subclasses()

        self.fields["collaborative_collections"].queryset = (
            Collection.objects.filter(
                Q(owner=user)
                | (
                    Q(collaborativecollection__collaborators__in=[user])
                    & Q(collaborativecollection__collaborator__status=1)
                )
            )
            .filter(collaborativecollection__isnull=False)
            .distinct()
        )
        self.fields["collaborative_collections"].initial = (
            instance.collection_set.filter(
                Q(owner=user)
                | (
                    Q(collaborativecollection__collaborators__in=[user])
                    & Q(collaborativecollection__collaborator__status=1)
                )
            )
            .filter(collaborativecollection__isnull=False)
            .distinct()
        )

    def clean(self):
        """Validate at least on element i selected."""
        collections = self.cleaned_data.get("collections")
        collaborative_collections = self.cleaned_data.get("collaborative_collections")
        if not (collections or collaborative_collections):
            raise forms.ValidationError(
                _("Debes seleccionar al menos una colección o colección colaborativa.")
            )
        return self.cleaned_data

    def save(self):
        """
        Sync collections to match the ones in the form.

        First remove the extra ones and then add the ones that should be kept.
        """
        final_collections = list(self.cleaned_data["collections"])
        existing_collections = list(self.fields["collections"].initial)
        collections_to_remove = [
            collection
            for collection in existing_collections
            if collection not in final_collections
        ]

        final_collaborative_collections = list(
            self.cleaned_data["collaborative_collections"]
        )
        existing_collaborative_collections = list(
            self.fields["collaborative_collections"].initial
        )
        collaborative_collections_to_remove = [
            collaborative_collection
            for collaborative_collection in existing_collaborative_collections
            if collaborative_collection not in final_collaborative_collections
        ]

        self.instance.collection_set.remove(
            *collections_to_remove, *collaborative_collections_to_remove
        )
        self.instance.collection_set.add(
            *final_collections, *final_collaborative_collections
        )
        # TODO: do this with signals
        mark_resource_for_reindex(self.instance)


class ReviewForm(forms.ModelForm):
    """Form for Reviews."""

    class Meta:
        """Define properties for ReviewForm class."""

        model = Review
        fields = ["title", "text", "rating"]

        widgets = {
            "rating": forms.RadioSelect(
                choices=(
                    (1, _("Chichipato")),
                    (2, _("Charro")),
                    (3, _("Chimbita")),
                    (4, _("Chévere")),
                    (5, _("Del chiras")),
                )
            )
        }

    def __init__(self, *args, **kwargs):
        """Set placeholders for fields."""
        super().__init__(*args, **kwargs)
        self.fields["title"].label = _("Título de la reseña")
        self.fields["title"].widget.attrs["placeholder"] = _(
            "Ingresa el título de la reseña."
        )
        self.fields["text"].label = _("Descripción")
        self.fields["text"].widget.attrs["placeholder"] = _(
            "Ingresa el texto aquí máximo %(max_length)d caracteres"
        ) % {"max_length": self.fields["text"].max_length}


class ReviewActionsForm(forms.Form):

    # TODO esto se va a reventar en algun momento, por favor pedir a David que lo corrija
    remove_review = forms.ModelChoiceField(
        queryset=Review.objects.select_related("resource").all(), required=False
    )

    def __init__(self, user, *args, **kwargs):
        """Set collections_group instance."""
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self):
        """Create Collaborators."""
        review = self.cleaned_data["remove_review"]
        if review and review.author == self.user:
            return Review.objects.filter(
                pk=self.cleaned_data["remove_review"].pk
            ).delete()


class CollectionForm(GetCollectionsGroupInitialMixin, FormNameMixin, forms.ModelForm):
    """Form to add Collections."""

    cropped_image = forms.CharField(required=False)

    collection_type = forms.ChoiceField(
        choices=COLLECTION_TYPE_CHOICES, widget=forms.RadioSelect, initial="private"
    )

    collaborative = forms.BooleanField(
        label=_("Colección colaborativa"), required=False
    )

    collections_groups = CollectionsGroupsField(
        label=_("Grupo"), queryset=None, required=False
    )

    collections_groups_checkboxes = ModelMultipleChoiceField(
        label=_("Mis Grupos"),
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        """Define properties for CollectionForm."""

        model = Collection
        fields = ["title", "description", "image", "default_cover_image", "public"]
        widgets = {"default_cover_image": forms.RadioSelect}

    def __init__(self, user, *args, **kwargs):
        """Set placeholders for fields and queryset for collections groups."""
        super().__init__(*args, **kwargs)

        self.fields["title"].widget.attrs["placeholder"] = _("Ingresa un nombre.")
        self.fields["default_cover_image"].required = False

        collections_groups_queryset = CollectionsGroup.objects.filter(owner=user)
        self.fields["collections_groups"].user = user
        self.fields["collections_groups"].queryset = collections_groups_queryset
        self.fields["collections_groups_checkboxes"].queryset = (
            collections_groups_queryset
        )

    @staticmethod
    def get_collection_form_initial(collection, users_groups=None):

        collection_is_collaborative = hasattr(collection, "collaborativecollection")
        collection_is_public = collection.public

        if collection_is_collaborative:
            initial_collection_type = COLLECTION_TYPE_CHOICES[0][0]
        elif collection_is_public:
            initial_collection_type = COLLECTION_TYPE_CHOICES[1][0]
        else:
            initial_collection_type = COLLECTION_TYPE_CHOICES[2][0]

        initial = {
            "collaborative": collection_is_collaborative,
            "collection_type": initial_collection_type,
        }

        if users_groups:
            initial.update(
                CollectionForm.get_collections_groups_form_initial(
                    collection, users_groups
                )
            )

        return initial

    def clean_public(self):
        """Set collection public or private."""
        is_private = self.data.get("collection_type") == COLLECTION_TYPE_CHOICES[2][0]
        return True if not is_private else False

    def clean_collaborative(self):
        """Set collection collaborative."""
        is_collaborative = (
            self.data.get("collection_type") == COLLECTION_TYPE_CHOICES[0][0]
        )
        return is_collaborative

    def clean_image(self):
        """Convert cropped_image to file and assign it to image field."""
        if "cropped_image" in self.changed_data:
            cropped_image = base64_file(self.data.get("cropped_image"))
            return cropped_image
        return self.cleaned_data["image"]

    def save(self, commit=True):
        """Extra actions after saving a collection.
        After:
            Convert a Collection into a Collaborative Collection and save the data.
            Set Collections Group relations.
        """
        if (
            "default_cover_image" in self.changed_data
            and "cropped_image" not in self.changed_data
        ):
            self.instance.image = None

        super().save(commit)

        if "collections_groups" in self.changed_data:
            if "collections_groups" in self.initial:
                user_initial_collections_groups = self.initial["collections_groups"]
                clear = True
            else:
                user_initial_collections_groups = None
                clear = True
            new_collections_groups = self.cleaned_data.get("collections_groups").all()
            collection = getattr(self.instance, "collection_ptr", self.instance)
            CollectionsGroupCollection.update_collection_groups(
                collection,
                new_collections_groups,
                clear=clear,
                initial_collections_group=user_initial_collections_groups,
            )

        if self.cleaned_data.get("collaborative"):
            self.instance = CollaborativeCollection.create_from_collection(
                self.instance
            )

        return self.instance


class BaseCollectionAddToGroupsFormSet(BaseFormSet):
    """Custom formset for collections add to groups form."""

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        if isinstance(index, int) and index < len(self.initial):
            kwargs["instance"] = self.initial[index]["instance"]
        else:
            kwargs["instance"] = index
        return kwargs


class CollectionAddToGroupsForm(
    GetCollectionsGroupInitialMixin, FormNameMixin, forms.Form
):
    collection = None

    collections_groups = CollectionsGroupsField(
        label=_("Grupo"), queryset=None, required=False
    )

    collections_groups_checkboxes = ModelMultipleChoiceField(
        label=_("Mis Grupos"),
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, instance, user, *args, **kwargs):
        """Set queryset for collections groups."""
        super().__init__(*args, **kwargs)

        queryset = CollectionsGroup.objects.filter(owner=user)
        self.fields["collections_groups"].user = user
        self.fields["collections_groups"].queryset = queryset
        self.fields["collections_groups_checkboxes"].queryset = queryset
        self.collection = instance

    def save(self, clear=True):
        """
        Set Collections Group relations.
        """
        if self.collection:
            user_initial_collections_groups = self.initial["collections_groups"]
            new_collections_groups = self.cleaned_data.get("collections_groups")
            result = CollectionsGroupCollection.update_collection_groups(
                self.collection,
                new_collections_groups,
                clear=clear,
                initial_collections_group=user_initial_collections_groups,
            )
            # TODO: do this with signals
            if len(result):
                mark_resource_for_reindex(self.collection)

            return result
        return None


class SetForm(GetCollectionsGroupInitialMixin, forms.ModelForm):
    """Form to add set to collections group."""

    collections_groups = CollectionsGroupsField(
        label=_("Grupo"), queryset=None, required=False
    )

    collections_groups_checkboxes = ModelMultipleChoiceField(
        label=_("Mis Grupos"),
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        """Define properties for CollectionForm."""

        fields = []
        model = Set

    def __init__(self, user, *args, **kwargs):
        """Set placeholders for fields."""
        super().__init__(*args, **kwargs)

        collections_groups_queryset = CollectionsGroup.objects.filter(owner=user)
        self.fields["collections_groups"].user = user
        self.fields["collections_groups"].queryset = collections_groups_queryset
        self.fields["collections_groups_checkboxes"].queryset = (
            collections_groups_queryset
        )

    def save(self, commit=True):
        """
        Set Collections Group relations.
        """
        if "collections_groups" in self.changed_data:
            user_initial_collections_groups = self.initial["collections_groups"]
            new_collections_groups = self.cleaned_data.get("collections_groups").all()
            CollectionsGroupCollection.update_collection_groups(
                self.instance,
                new_collections_groups,
                initial_collections_group=user_initial_collections_groups,
            )
        return self.instance


class CollectionsGroupForm(forms.ModelForm):
    """Form to add Collections Groups."""

    class Meta:
        """Define properties for CollectionForm."""

        fields = ["title"]
        model = CollectionsGroup

    def __init__(self, *args, **kwargs):
        """Set placeholders for fields."""
        super().__init__(*args, **kwargs)

        self.fields["title"].widget.attrs["placeholder"] = _("Ingresa un nombre.")

    def clean_title(self):
        """Raise validation error for non unique title."""
        title = self.cleaned_data.get("title").lower()
        title_exist = CollectionsGroup.objects.filter(
            title=title, owner=self.instance.owner
        ).exists()
        if title_exist and title == "favoritos":
            raise forms.ValidationError(
                _(
                    "Ya tienes un grupo de colecciones llamado favoritos, lo puedes ver "  # noqa: E501
                ),
                code="favorites",
            )
        elif title_exist:
            raise forms.ValidationError(
                _(
                    "Ya tienes un grupo de colecciones con este nombre, "
                    "elige un nombre diferente e intentalo de nuevo."
                )
            )
        return title


class CollaborativeCollectionForm(CollectionForm):
    """Form to edit Collaborative Collections."""

    class Meta(CollectionForm.Meta):
        """Define properties for CollaborativeCollectionForm."""

        fields = [
            "title",
            "description",
            "image",
            "public",
            "collaborative",
            "collaborators",
            "default_cover_image",
        ]
        model = CollaborativeCollection
        widgets = {
            "collaborators": forms.CheckboxSelectMultiple,
            "default_cover_image": forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        """Replace queryset for collaborators field."""
        super().__init__(*args, **kwargs)
        self.fields["collaborators"].queryset = self.instance.collaborators.all()

    def save(self, commit=True):
        """Convert a Collaborative Collection to Collection and save de data."""
        super().save(commit)
        if not self.cleaned_data.get("collaborative"):
            collection = self.instance.collection_ptr
            self.instance.delete(keep_parents=True)
            self.instance = collection
        return self.instance


class CollectionsCollaboratorsForm(forms.Form):
    """Form to edit Collections Collaborators."""

    collaborators = forms.CharField(
        label=_("Personas seleccionadas para invitar"), required=False
    )

    def __init__(self, object, request, *args, **kwargs):
        """Set CollaborativeCollection instance."""
        super().__init__(*args, **kwargs)
        self.collaborative_collection = object
        self.request = request

    def clean_collaborators(self):
        """Check if given form user's ids can be collaborators of a Collection."""
        data = self.cleaned_data["collaborators"]
        collaborators = data.strip().split(",")
        valid_users = self.get_valid_users_queryset(
            self.collaborative_collection
        ).filter(pk__in=collaborators)

        if valid_users.count() != len(collaborators):
            raise forms.ValidationError(_("No puede invitar a estos Colaboradores"))
        instances = [
            Collaborator(
                user=user,
                collaborativecollection=self.collaborative_collection,
                status=-1,
            )
            for user in valid_users
        ]
        for instance in instances:
            instance.full_clean()
        return instances

    def save(self):
        """Create Collaborators."""
        collaborators = Collaborator.objects.bulk_create(
            self.cleaned_data["collaborators"]
        )
        self.notify_collaborators(collaborators)

    @staticmethod
    def get_valid_users_queryset(collaborative_collection):
        """Return a QuerySet of valid Users to Invite."""
        return User.objects.exclude(
            collaborativecollection=collaborative_collection
        ).exclude(pk=collaborative_collection.owner.pk)

    def notify_collaborators(self, collaborators):
        """
        Envía un mail de notificación al usuario invitado.

        Una vez que un usuario invite a otro a colaborar en una colección
        se le envía un email de notificación al usuario
        invitado.

        """
        email_body = self.get_notify_collaborators_email_body()
        messages = []
        for collaborator in collaborators:
            messages.append(
                (
                    self.get_notify_collaborators_email_subject(),
                    email_body["plain_text"],
                    email_body["html"],
                    None,
                    [collaborator.user.email],
                )
            )
        send_mass_html_mail(tuple(messages), fail_silently=False)

    def get_notify_collaborators_email_subject(self):
        """Retorna el subject del email de invitación a una colección colaborativa."""
        return loader.render_to_string(
            "harvester/email/notify_collaborators_subject.txt",
            {
                "collaborative_collection": self.collaborative_collection,
                "inviter": self.request.user,
            },
            self.request,
        ).strip()

    def get_notify_collaborators_email_body(self):
        """Retorna el cuerpo del email de invitación para una colección colaborativa."""
        html_body = loader.render_to_string(
            "harvester/email/notify_collaborators_body.html",
            {
                "collaborative_collection": self.collaborative_collection,
                "inviter": self.request.user,
            },
            self.request,
        )
        plain_text_body = loader.render_to_string(
            "harvester/email/notify_collaborators_body.txt",
            {
                "collaborative_collection": self.collaborative_collection,
                "inviter": self.request.user,
            },
            self.request,
        ).strip()
        return {"plain_text": plain_text_body, "html": html_body}


class ContentResourceFilters(FiltersForm):
    """Filters for ContentResource querysets."""

    FIELDS_LOOKUPS = {
        "online": "data_source__online_resources",
        "subject": "subject__equivalence__in",
        "content_type": "type__equivalence__in",
    }
    online = forms.ChoiceField(
        label=_("Disponibilidad"),
        choices=ONLINE_RESOURCES_CHOICES,
        required=False,
        widget=forms.RadioSelect,
    )
    subject = EquivalenceMultipleChoiceField(
        label=_("Tema"), field="subject", required=False
    )
    content_type = EquivalenceMultipleChoiceField(
        label=_("Tipo de contenido"),
        field="type",
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )


class SetFilters(FiltersForm):
    """Filters for Set querysets."""

    FIELDS_LOOKUPS = {"data_source": "data_source__in"}
    data_source = forms.ModelMultipleChoiceField(
        label=_("Fuente"), queryset=DataSource.objects.all(), required=False
    )


class ContentResourceActionsForm(FormNameMixin, forms.Form):
    """Form to delete a ContentResource from a Collection."""

    remove_resource = forms.ModelChoiceField(queryset=None, required=False)
    collaborate = forms.NullBooleanField(initial=None, required=False, disabled=True)

    def __init__(self, collection, user, *args, **kwargs):
        """Set CollaborativeCollection instance."""
        super().__init__(*args, **kwargs)
        self.collection = collection
        self.user = user
        self.fields["remove_resource"].queryset = ContentResource.objects.filter(
            collection=collection
        )

        try:
            collaborative_collection = collection.collaborativecollection
        except CollaborativeCollection.DoesNotExist:
            pass
        else:
            self.fields["collaborate"].disabled = False
            self.fields["collaborate"].initial = (
                collaborative_collection.collaborators.filter(
                    collaborator__user__in=[user], collaborator__status=1
                ).exists()
            )

    def save(self):
        """Create Collaborators."""
        if self.cleaned_data["remove_resource"]:
            CollectionAndResource.objects.filter(
                collection=self.collection,
                resource_id=self.cleaned_data["remove_resource"],
            ).delete()
            return

        if self.cleaned_data["collaborate"] is not None:
            if self.cleaned_data["collaborate"]:
                collaborator = Collaborator.objects.get_or_create(
                    collaborativecollection=self.collection.collaborativecollection,
                    user=self.user,
                    defaults={"status": -2},
                )[0]
                collaborator.save()
            else:
                Collaborator.objects.filter(
                    collaborativecollection=self.collection.collaborativecollection,
                    user=self.user,
                ).delete()


class CollectionActionsForm(forms.Form):
    """Form to delete a Collection from a Collections Group."""

    remove_collection = forms.CharField(required=False)

    def __init__(self, collections_group, user, *args, **kwargs):
        """Set collections_group instance."""
        super().__init__(*args, **kwargs)
        self.collections_group = collections_group
        self.user = user

    def save(self):
        """Save form."""
        if self.cleaned_data["remove_collection"]:
            collection_pk, collection_model_name, collection_app_label = [
                data for data in self.cleaned_data["remove_collection"].split("-")
            ]
            try:
                collection_content_type = ContentType.objects.get_by_natural_key(
                    collection_app_label, collection_model_name
                )
            except ContentType.DoesNotExist:
                collection_content_type = None

            if collection_content_type and collection_model_name:
                CollectionsGroupCollection.objects.filter(
                    content_type=collection_content_type,
                    object_pk=collection_pk,
                    collections_group=self.collections_group,
                ).delete()
                return


class DataSourceAdminForm(ModelForm):
    """Custom form for Data Source Config in Admin."""

    config = DataSourceConfigField(
        label=DataSource._meta.get_field("config").verbose_name
    )
    dynamic_image = DynamicUrlField(
        required=False, label=DataSource._meta.get_field("dynamic_image").verbose_name
    )

    class Meta:
        """Set options for DataSourceAdminForm."""

        model = DataSource
        fields = "__all__"


class DynamicIdentifierConfigInlineForm(ModelForm):
    """Custom form for Data Source Config in Admin."""

    field = forms.ChoiceField(
        choices=((None, _("Seleccione un Campo")),)
        + tuple(DUBLIN_CORE_DEFAULT_ASSOCIATION),
        label=_("Campo Dublin Core"),
    )
    capture_expression = CaptureExpressionField(
        label=_("Acción de Captura"),
        validators=[validators.RegexValidator],
    )

    class Meta:
        """Set options for DynamicIdentifier Inline Form."""

        model = DynamicIdentifierConfig
        fields = "__all__"

    class Media:
        """Set Media options for DynamicIdentifier Inline Form."""

        js = ("harvester/js/dynamic_identifier_inline.js",)


class ShareContentResourceForm(forms.Form):
    """Form to edit Collections Collaborators."""

    users = forms.CharField(
        label=_("Personas seleccionadas para compartir"), required=False
    )

    def __init__(self, object, request, *args, **kwargs):
        """Set CollaborativeCollection instance."""
        super().__init__(*args, **kwargs)
        self.content_resource = object
        self.request = request

    def clean_users(self):
        """Check if the resource can be shared with the given form user's ids."""
        data = self.cleaned_data["users"]
        users = data.strip().split(",")
        valid_users = self.get_valid_users_queryset(
            the_sharing_user=self.request.user,
            time_filter=True,
            resource=self.content_resource,
        ).filter(pk__in=users)

        if valid_users.count() != len(users):
            raise forms.ValidationError(
                _("No puedes compartir el recurso con todos estos usuarios")
            )

        return valid_users

    def save(self):
        """Save method."""
        users = self.cleaned_data["users"]
        shared_resource_register = SharedResource.objects.get_or_create(
            owner=self.request.user, resource=self.content_resource
        )[0]
        new_objects_list = []
        for user in users:
            new_objects_list.append(
                SharedResourceUser(shared_resource=shared_resource_register, user=user)
            )
        if new_objects_list:
            SharedResourceUser.objects.bulk_create(new_objects_list)
            self.notify_users(users)

    @staticmethod
    def get_valid_users_queryset(
        the_sharing_user,
        time_filter=True,
        resource=None,
    ):
        """Return a QuerySet of valid Users to share the resource with."""
        user_qs = User.objects.exclude(pk=the_sharing_user.pk)
        if time_filter:
            try:
                # If shared_resource exists, filter queryset by users
                # who have been shared within less than 24 hours
                yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
                shared_resource_users = SharedResourceUser.objects.filter(
                    shared_resource__owner=the_sharing_user,
                    shared_resource__resource=resource,
                    created_at__gt=yesterday,
                )
                user_qs.exclude(
                    sharedresourceuser__in=shared_resource_users,
                )
            except SharedResource.DoesNotExist:
                pass
        return user_qs

    def notify_users(self, users):
        """Envía un mail de notificación de recurso compartido al usuario."""
        email_body = self.get_notify_users_email_body()
        messages = []
        for user in users:
            messages.append(
                (
                    self.get_notify_users_email_subject(),
                    email_body["plain_text"],
                    email_body["html"],
                    None,
                    [user.email],
                )
            )
        send_mass_html_mail(tuple(messages), fail_silently=False)

    def get_notify_users_email_subject(self):
        """Retorna el subject del email de recurso compartido."""
        return loader.render_to_string(
            "harvester/email/notify_users_subject.txt",
            {
                "resource": self.content_resource,
                "the_sharing_user": self.request.user,
            },
            self.request,
        ).strip()

    def get_notify_users_email_body(self):
        """Retorna el cuerpo del email de recurso compartido."""
        html_body = loader.render_to_string(
            "harvester/email/notify_users_body.html",
            {
                "resource": self.content_resource,
                "the_sharing_user": self.request.user,
            },
            self.request,
        )
        plain_text_body = loader.render_to_string(
            "harvester/email/notify_users_body.txt",
            {
                "resource": self.content_resource,
                "the_sharing_user": self.request.user,
            },
            self.request,
        ).strip()
        return {"plain_text": plain_text_body, "html": html_body}
