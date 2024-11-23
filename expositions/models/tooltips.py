from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet

from expositions.editors import MiniEditor

TOOLTIP_CHOICES = [
    ("simple_search", _("Búsqueda simple")),
    ("advanced_search", _("Búsqueda avanzada")),
    ("collection_groups", _("Grupos de las colecciones")),
    ("collection_groups_creation", _("Crear grupo de colecciones")),
    ("favorites", _("Colecciones favoritas")),
    ("collection_creation", _("Crear colección")),
    ("exposition_timeline", _("Exposiciones linea del tiempo")),
    ("exposition_map", _("Exposiciones mapa")),
    ("login", _("Registro y login")),
    ("profile_image", _("Perfil: foto recorte de imágenes")),
]


@register_snippet
class Tooltip(models.Model):

    name = models.CharField(max_length=255, verbose_name=_("Nombre"))
    description = RichTextField(
        max_length=255, verbose_name=_("Texto Tooltip"), features=MiniEditor.FEATURES
    )
    page = models.CharField(
        max_length=255, verbose_name=_("Página"), choices=TOOLTIP_CHOICES
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("page"),
    ]

    def __str__(self):
        """A readable representation."""
        return self.name

    def clean(self):
        super().clean()
        if Tooltip.objects.filter(page=self.page).exists() and self._state.adding:
            raise ValidationError("Ya existe un tooltip para la página seleccionada.")

    class Meta:
        verbose_name = _("Tooltip")
        verbose_name_plural = _("Tooltips")
