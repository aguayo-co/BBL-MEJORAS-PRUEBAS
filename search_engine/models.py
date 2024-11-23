"""Definición de modelos para la aplicación search_engine."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class IndexedResource(models.Model):
    """Modelo de recursos indexados en elasticsearch."""

    indexed_at = models.DateTimeField(verbose_name="indexed at")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    need_to_index = models.BooleanField(default=False)

    def __str__(self):
        """Representación en string de las instancias del modelo."""
        return f"{self.indexed_at} - {self.object_id} - {self.content_type}"

    class Meta:
        """Define propiedades personalizadas para el modelo IndexedResource."""

        verbose_name = _("recurso indexado")
        verbose_name_plural = _("recursos indexados")
        unique_together = (("content_type", "object_id"),)
        indexes = [
            models.Index(fields=["object_id"]),
            models.Index(fields=["need_to_index"]),
            models.Index(fields=["indexed_at"]),
        ]
