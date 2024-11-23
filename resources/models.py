"""Define models for Resources app."""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampModel(models.Model):
    """Base class with control fields (creation/update)."""

    created_at = models.DateTimeField(verbose_name=_("creado el"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("actualizado el"), auto_now=True)
    to_delete = models.BooleanField(
        verbose_name=_("Borrado programado"), null=True, default=False
    )

    class Meta:
        """Define some custom properties for TimestampModel."""

        abstract = True

        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["updated_at"])]


class ValidateFileMixin:
    """Mixin to validate files for file fields exist."""

    def full_clean(self, exclude=None, validate_unique=True):
        """Exclude from validation file fields where file does not exists."""
        fields = [
            field
            for field in self._meta.get_fields()
            if isinstance(field, models.FileField)
        ]

        for field in fields:
            data = getattr(self, field.attname)
            if not data:
                continue

            try:
                data.file
            except IOError:
                exclude = (exclude or set()).union({field.name})

        super().full_clean(exclude, validate_unique)

    def clean(self):
        """Remove the path to the file if it does not exist."""
        fields = [
            field
            for field in self._meta.get_fields()
            if isinstance(field, models.FileField)
        ]
        errors = {}
        msg = _(
            "El archivo no se encuentra. Intenta nuevamente, y si el error persiste,"
            " por favor sube uno nuevo."
        )

        for field in fields:
            data = getattr(self, field.attname)
            if not data:
                continue

            try:
                data.file
            except IOError:
                errors[field.name] = msg

        if errors:
            raise ValidationError(errors)
