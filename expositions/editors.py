"""Define bloques y componentes de edición de texto."""
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.blocks import BooleanBlock


class FullEditor(blocks.RichTextBlock):
    """Editor con configuración completa."""

    FEATURES = [
        "h2",
        "h3",
        "bold",
        "italic",
        "ol",
        "ul",
        "hr",
        "link",
        "document-link",
        "image",
        "embed",
        "superscript",
        "subscript",
        "blockquote",
    ]

    def __init__(self, **kwargs):
        """Inserta `features` en las variables de inicialización."""
        if "features" in kwargs.keys():
            kwargs.pop("features")
        super().__init__(features=self.FEATURES, **kwargs)

    class Meta:
        """Define opciones para FullEditor."""

        label = _("editor de texto")


class MiniEditor(FullEditor):
    """Editor con configuración limitada."""

    FEATURES = [
        "h3",
        "h4",
        "bold",
        "italic",
        "ol",
        "ul",
        "hr",
        "link",
        "superscript",
        "subscript",
        "blockquote",
    ]

    class Meta:
        """Define opciones para MiniEditor."""

        label = _("mini editor")


class FullEditorBlock(blocks.StructBlock):
    """Editor que permite mostrar/ocultar el separador de contexto."""

    title = blocks.TextBlock(
        max_length=150,
        verbose_name=_("Titulo"),
        required=False,
    )
    intro = blocks.TextBlock(
        max_length=200,
        verbose_name=_("Introducción"),
        required=False,
    )
    show_context_delimiter = BooleanBlock(
        label="Mostrar delimitador de contexto",
        default=True,
        null=True,
        help_text=_("muestra una línea delimitadora antes de este componente."),
        required=False,
    )
    wysiwyg = FullEditor()

    class Meta:
        """Define opciones para MiniEditor."""

        label = _("texto enriquecido")
        template = "expositions/component/free_content_component.html"


class LimitedEditor(FullEditor):
    """Editor con configuración limitada para lista de avatares."""

    FEATURES = [
        "bold",
        "italic",
        "h2",
        "h3",
        "hr",
        "link",
    ]

    class Meta:
        """Define opciones para MiniEditor."""

        label = _("Editor Limitado")
