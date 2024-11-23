"""Define Fields for resources app."""

import bleach
from ckeditor.fields import RichTextField
from django.core import validators
from django.core.validators import FileExtensionValidator, ValidationError
from django.db import models
from django.db.models import Q, JSONField
from django.forms import CharField
from django.forms import ImageField as DjangoImageField
from django.forms import Textarea
from django.utils import timezone
from functools import partial as curry
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .validators import FileSizeValidator, validate_toml


class TomlField(CharField):
    """A field that validates its content is valid TOML."""

    widget = Textarea
    default_validators = [validate_toml]


class ImageField(DjangoImageField):
    """A field that validates file size and extensions."""

    default_validators = [
        FileSizeValidator(1000000),
        FileExtensionValidator(["jpg", "jpeg", "png"]),
    ]


class WysiwygField(RichTextField):
    """Field with a Wysiwyg Editor, works as a TextField, but clean the content."""

    TAGS = {
        "strong": [],
        "b": [],
        "em": [],
        "u": [],
        "s": [],
        "sub": [],
        "sup": [],
        "ol": [],
        "li": [],
        "ul": [],
        "p": ["style"],
        "br": [],
        "a": ["href", "target"],
    }

    def from_db_value(self, value, *_):
        """Return the Bleach cleaned string as safe to be used in app's templates."""
        if value:
            return mark_safe(self.bleach_clean(value))
        return value

    def pre_save(self, model_instance, add):
        """Return the Bleach cleaned value before save in database."""
        value = super().pre_save(model_instance, add)
        value = self.bleach_clean(value)
        setattr(model_instance, self.attname, value)
        return value

    def bleach_clean(self, value):
        """Clean an HTML fragment of malicious content and return it."""
        return bleach.clean(
            value, tags=self.TAGS.keys(), attributes=self.TAGS, strip=True
        )

    def validate(self, value, model_instance):
        """Extend validation to check for HTML safety."""
        super().validate(value, model_instance)

        if not value:
            return

        normalized_value = (
            value.replace("<br />", "<br>").replace("\r\n", "\n").replace("\r", "\n")
        )
        cleaned_value = self.bleach_clean(value)

        if normalized_value != cleaned_value:
            raise ValidationError(
                _("Has usado etiquetas o atributos HTML no permitidos.")
            )


class CachedFieldMixin:
    """Field with cached value, if it has expired is updated in the background."""

    name = None

    def __init__(self, *args, **kwargs):
        """Set Field parameters."""
        self.init_args = args
        self.init_kwargs = kwargs

        # cached fields are not editable from the administrator
        kwargs.update({"editable": False})
        super().__init__(*args, **kwargs)

    def contribute_to_class(
        self, cls, name, private_only=False
    ):  # pylint: disable=unused-argument
        """Bound attrs to the parent container class."""
        self.name = name
        # Add field's Getters and Setters
        setattr(
            cls,
            name,
            property(
                curry(self._get_field, field=self), curry(self._set_field, field=self)
            ),
        )

        # Add Update Method for current field
        update_method_name = f"update_cached_{self.name}"
        if not hasattr(cls, update_method_name):
            setattr(cls, update_method_name, self.update_cached_field)

        # Add method to generate fields filters
        if not hasattr(cls, "get_cached_field_expired_filters"):
            cls.get_cached_field_expired_filters = self.get_cached_field_expired_filters

        # Add Expired Instances Method
        if not hasattr(cls, "get_expired_instances"):
            cls.get_expired_instances = classmethod(self.get_expired_instances)

        # Add method to get cached fields
        if not hasattr(cls, "get_cached_fields"):
            cls.get_cached_fields = classmethod(self.get_cached_fields)

        # Add method to get updated fields
        if not hasattr(cls, "get_updated_cached_fields"):
            cls.get_updated_cached_fields = classmethod(self.get_updated_cached_fields)

        # Add Update Method for all fields
        if not hasattr(cls, "update_expired_fields"):
            cls.update_expired_fields = self.update_expired_fields

        # Add Real field
        cached_field_name = f"{self.name}_cached"
        real_field = self.base_class()(*self.init_args, **self.init_kwargs)
        setattr(cls, cached_field_name, real_field)
        real_field.contribute_to_class(cls, cached_field_name)

        # Add Expiration Date Field
        expiration_date_field_name = f"{self.name}_expiration"
        expiration_date_field = models.DateTimeField(null=True, editable=False)
        setattr(cls, expiration_date_field_name, expiration_date_field)
        expiration_date_field.contribute_to_class(cls, expiration_date_field_name)

        # Add Is Expired Field
        expired_field_name = f"{self.name}_expired"
        expired_field = models.BooleanField(default=True, null=True, editable=False)
        setattr(cls, expired_field_name, expired_field)
        expired_field.contribute_to_class(cls, expired_field_name)

    @staticmethod
    def base_class():
        """Datatype for the current Field."""
        return models.CharField

    @staticmethod
    def get_cached_fields(model):
        """Return a list of cached fields in this model."""
        return [
            field.name
            for field in model._meta.get_fields(include_parents=True)
            if field.name.endswith("_cached")
        ]

    @staticmethod
    def get_updated_cached_fields(model):
        """Return all cached-field related fields in this model."""
        base_fields = model.get_cached_fields()
        fields = []
        for field in base_fields:
            fields.append(field)
            field_name = field.replace("_cached", "")
            fields.append(f"{field_name}_expired")
            fields.append(f"{field_name}_expiration")
        return fields + ["updated_at"]

    @staticmethod
    def _set_field(model, val, field=None):
        """Setter for the field, overwrites the Model setter only for this field."""
        setattr(model, f"{field.name}_cached", val)

    @staticmethod
    def _get_field(model, field=None):
        """Getter for the field, overwrites the Model getter only for this field."""
        return getattr(model, f"{field.name}_cached")

    def update_cached_field(self):
        """Model must implement this method with the given name."""
        raise NotImplementedError(
            f"Model must implement update_cached_{self.name} method"
        )

    @staticmethod
    def update_expired_fields(model_instance):
        """Run the update method for each cached field."""
        methods = [
            name for name in dir(model_instance) if name.startswith("update_cached_")
        ]
        for method in methods:
            getattr(model_instance, method)()

    @staticmethod
    def get_cached_field_expired_filters(field):
        """Return a list of filters to get instances with the given field expired."""
        filters = Q()
        filters |= Q(**{f"{field}_expired": True})
        filters |= Q(**{f"{field}_expired__isnull": True})
        filters |= Q(**{f"{field}_expiration__isnull": True})
        filters |= Q(**{f"{field}_expiration__lt": timezone.now()})
        return filters

    @staticmethod
    def get_expired_instances(model):
        """Return model instances that contain expired cached fields."""
        fields = [field.replace("_cached", "") for field in model.get_cached_fields()]
        filters = Q()
        for field in fields:
            filters |= model.get_cached_field_expired_filters(field)
        return model.objects.filter(filters)

    def deconstruct(self):
        """Return enough information to recreate the field as a 4-tuple."""
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs


class IntegerCachedField(
    CachedFieldMixin, models.IntegerField
):  # pylint: disable=abstract-method
    """Cached Field implementation for Integer DataType."""

    @staticmethod
    def base_class():
        """Datatype for the current Field."""
        return models.IntegerField


class TextCachedField(
    CachedFieldMixin, models.TextField
):  # pylint: disable=abstract-method
    """Cached Field implementation for Text Datatype."""

    @staticmethod
    def base_class():
        """Datatype for the current Field."""
        return models.TextField


class JSONCachedField(CachedFieldMixin, JSONField):
    """Cached field implementation for JSONField."""

    @staticmethod
    def base_class():
        return JSONField


class LatitudeField(models.DecimalField):
    """A Field to store Geospatial Latitude."""

    default_validators = [
        validators.MaxValueValidator(90),
        validators.MinValueValidator(-90),
    ]
    max_digits = 8
    decimal_places = 6

    def __init__(self, verbose_name=None, name=None, **kwargs):
        try:
            kwargs.pop("max_digits")
            kwargs.pop("decimal_places")
        except KeyError:
            pass

        super().__init__(
            verbose_name,
            name,
            max_digits=self.max_digits,
            decimal_places=self.decimal_places,
            **kwargs,
        )


class LongitudeField(models.DecimalField):
    """A Field to store Geospatial Longitude."""

    default_validators = [
        validators.MaxValueValidator(180),
        validators.MinValueValidator(-180),
    ]
    max_digits = 9
    decimal_places = 6

    def __init__(self, verbose_name=None, name=None, **kwargs):
        try:
            kwargs.pop("max_digits")
            kwargs.pop("decimal_places")
        except KeyError:
            pass

        super().__init__(
            verbose_name,
            name,
            max_digits=self.max_digits,
            decimal_places=self.decimal_places,
            **kwargs,
        )
