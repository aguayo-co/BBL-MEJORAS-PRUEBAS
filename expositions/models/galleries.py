"""Define WagTail snippets for expositions app."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.blocks import StreamBlock
from wagtail.fields import StreamField
from wagtail.images import get_image_model
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet

from expositions.edit_handlers import VideoBlock


@register_snippet
class ImageGallery(ClusterableModel):
    """Define an Image Gallery."""

    name = models.CharField(max_length=255, unique=True, verbose_name=_("Nombre"))
    description = models.TextField(blank=True, verbose_name=_("Descripción"))

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        InlinePanel("images", min_num=1, max_num=6, label=_("imágenes")),
    ]

    class Meta:
        """Define some custom properties for Galleries."""

        verbose_name = _("Galería de Imágenes")
        verbose_name_plural = _("Galerías de Imágenes")

    def __str__(self):
        """Return the gallery name."""
        return self.name


class GalleryImage(Orderable):
    """Define an intermediate model for an Image and an Image Gallery."""

    gallery = ParentalKey(ImageGallery, related_name="images")
    image = models.ForeignKey(
        get_image_model(),
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("imagen"),
    )

    panels = [FieldPanel("image")]


@register_snippet
class VideoGallery(models.Model):
    """Define a Video Gallery."""

    name = models.CharField(max_length=255, unique=True, verbose_name=_("Nombre"))
    description = models.TextField(blank=True, verbose_name=_("Descripción"))
    videos = StreamField(StreamBlock([("video", VideoBlock(label="video"))], max_num=6), use_json_field=True)

    panels = [FieldPanel("name"), FieldPanel("description"), FieldPanel("videos")]

    class Meta:
        """Define some custom properties for Galleries."""

        verbose_name = _("Galería de Videos")
        verbose_name_plural = _("Galerías de Videos")

    def __str__(self):
        """Return the gallery name."""
        return self.name
