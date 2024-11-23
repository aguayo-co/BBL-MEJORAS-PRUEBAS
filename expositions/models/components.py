"""Define blocks & components for expositions app."""
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _
from wagtail.blocks import (
    BooleanBlock,
    CharBlock,
    ChoiceBlock,
    ListBlock,
    PageChooserBlock,
    RichTextBlock,
    StaticBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    URLBlock,
)
from wagtail.images.blocks import ImageChooserBlock

from expositions.blocks import UserChooserBlock

from expositions.edit_handlers import VideoBlock
from expositions.editors import LimitedEditor


class LinkToContentPagesComponent(StructBlock):
    title = CharBlock(required=False)
    subtitle = CharBlock(required=False)
    links = ListBlock(
        PageChooserBlock(
            page_type=(
                "expositions.ContentPage",
                "expositions.Redirection",
                "expositions.Exposition",
                "expositions.HelpCenterPage",
                "expositions.QuestionPage",
                "expositions.ThemePage",
            ),
            label=_("Página"),
            help_text=_("Página de contenido"),
        ),
        label=_("Enlaces"),
        help_text=_("Páginas de contenido a las que enlazar"),
        min_num=1,
        max_num=4,
    )

    class Meta:
        icon = "link"
        template = "expositions/components/link_to_content_pages.html"
        label = _("Enlaces a páginas de contenido")


class SlideContent(StreamBlock):
    image = ImageChooserBlock(
        label=_("Imagen"),
        help_text=_("Formato: 16:9, ancho: 960px, Alto:540px"),
    )
    video = VideoBlock(
        label=_("Vídeo"),
        help_text=_("Formato: 16:9"),
    )
    background = ImageChooserBlock(
        label=_("Imagen de fondo"),
        help_text=_("Dimensiones recomendadas Ancho 1440px, Alto: 575px"),
    )


class HeroSliderComponent(StructBlock):
    """
    A block that displays a slide image.
    """

    subtitle = CharBlock(required=False, label=_("Subtítulo"))
    title = LimitedEditor(required=False, label=_("Título"))
    description = LimitedEditor(required=False, label=_("Descripción"))
    slide_content = SlideContent(
        required=True,
        max_num=1,
        label=_("Contenido multimedia del slide (Solo permite una opción)"),
    )
    primary_action_text = CharBlock(required=False, label=_("Texto acción primaria"))
    primary_action_url = PageChooserBlock(
        required=False, label=_("URL acción primaria")
    )

    def clean(self, value):
        """Cta validation."""
        result = super().clean(value)
        errors = {}
        if value["primary_action_text"] and not value["primary_action_url"]:
            errors["primary_action_url"] = ErrorList(
                [
                    _(
                        "Ha definido un Texto para el botón de acción primaria, por tanto debe seleccionar una pagina."
                    )
                ]
            )
        if errors:
            raise ValidationError(errors)
        return result

    class Meta:
        icon = "image"
        label = _("Slide")
        template = "expositions/components/hero_slider_component.html"


class HelpCard(StructBlock):
    LOGO_CHOICES = (
        ("3d", _("Ícono 3D")),
        ("audio", _("Ícono Audio")),
        ("bdb", _("Ícono BDB")),
        ("biblored", _("Ícono Biblored")),
        ("search", _("Ícono Buscador")),
        ("compass", _("Ícono Brújula")),
        ("brochure", _("Ícono Brochure")),
        ("consult-contents", _("Ícono Consultar")),
        ("create", _("Ícono Crear")),
        ("copy", _("Ícono Copiar")),
        ("newsletter", _("Ícono Correo Electrónico")),
        ("collaborate", _("Ícono Colaborar")),
        ("share", _("Ícono Compartir")),
        ("contents-related", _("Ícono Contenido Relacionado")),
        ("quote", _("Ícono Comillas")),
        ("exclusive", _("Ícono Contenido Exclusivo")),
        ("interactive", _("Ícono Contenido Interactivo")),
        ("sketch", _("Ícono Diamante")),
        ("data", _("Ícono Datos")),
        ("doc", _("Ícono Documento")),
        ("digital", _("Ícono Digital")),
        ("star", _("Ícono Estrella")),
        ("photographs", _("Ícono Fotografías")),
        ("collective", _("Ícono Grupo de Personas")),
        ("study-guide", _("Ícono Guía de Estudio")),
        ("history", _("Ícono Historia")),
        ("person-following", _("Ícono Persona")),
        ("pen", _("Ícono Lápiz")),
        ("book", _("Ícono Libro")),
        ("map", _("Ícono Mapa")),
        ("megaphone", _("Ícono Megáfono")),
        ("monograph", _("Ícono Monografía")),
        ("narrative", _("Ícono Narrativa")),
        ("music-sheet", _("Ícono Nota Musical")),
        ("physical-objects", _("Ícono Objetos Físicos")),
        ("newspaper", _("Ícono Periódico")),
        ("personal", _("Ícono Persona")),
        ("story", _("Ícono Pergamino")),
        ("user", _("Ícono Persona redondeada")),
        ("software", _("Ícono Software")),
        ("texts", _("Ícono Textos")),
        ("thesis", _("Ícono Tesis")),
        ("location", _("Ícono Ubicación")),
        ("video", _("Ícono Video")),
        ("travel", _("Ícono Viaje")),
    )

    title = CharBlock(required=True, label=_("Título"))
    logo = ChoiceBlock(
        required=True,
        label=_("Logo"),
        choices=LOGO_CHOICES,
    )
    description = TextBlock(required=False, label=_("Descripción"), max_length=70)
    url = PageChooserBlock(required=True, label=_("URL"))


class HelpBlockComponent(StructBlock):
    title = CharBlock(required=True, label=_("Título"))
    subtitle = CharBlock(required=False, label=_("Subtítulo"))
    cards = ListBlock(
        HelpCard(),
        required=False,
        label=_("Tarjetas"),
        min_num=3,
        max_num=4,
    )

    class Meta:
        icon = "help"
        label = _("Bloque de ayuda")
        template = "expositions/components/help_block_component.html"


class UserComponent(StructBlock):
    user = UserChooserBlock(required=True, label=_("Seleccione un usuario del sistema")
    )
    subtitle = CharBlock(
        required=True,
        label=_("Cargo o subtítulo del avatar"),
        max_length=50,
        help_text=_("Recuerda no colocar un subtítulo de más de 50 caracteres"),
    )
    extra_info = CharBlock(
        required=False,
        label=_("Información adicional del avatar"),
        max_length=50,
        help_text=_(
            "Recuerda no colocar información adicional del avatar de más de 50 caracteres"
        ),
    )


class CustomUserComponent(StructBlock):
    image = ImageChooserBlock()
    title = CharBlock(
        required=True,
        label=_("Nombre o título del avatar"),
        max_length=50,
        help_text=_("Recuerda no colocar un subtítulo de más de 50 caracteres"),
    )
    subtitle = CharBlock(
        required=True,
        label=_("Cargo o subtítulo del avatar"),
        max_length=50,
        help_text=_("Recuerda no colocar un subtítulo de más de 50 caracteres"),
    )
    extra_info = CharBlock(
        required=False,
        label=_("Información adicional del avatar"),
        max_length=50,
        help_text=_(
            "Recuerda no colocar información adicional del avatar de más de 50 caracteres"
        ),
    )
    url = URLBlock(
        help_text=_("Puedes agregar al avatar un link externo"), required=False
    )


class AvatarListComponent(StructBlock):
    """Define una listado de imágenes."""

    title = CharBlock(label=_("Título de Sección"))
    type = ChoiceBlock(
        label=_("Visualización"),
        choices=(("text", _("Sin imágenes")), ("image", _("Con imágenes"))),
        default="text",
    )
    avatar_list = StreamBlock(
        [("user", UserComponent()), ("custom_user", CustomUserComponent())],
        label=_("Tipos de usuario"),
        help_text=_(
            "Selecciona el tipo Usuario del Sistema si deseas traer un usuario de la Bibliteca Digital de Bogota, "
            "de lo contrario puedes crear un avatar desde cero "
        ),
    )
    info = LimitedEditor(label=_("Subsección de información"), required=False)

    class Meta:
        """Define propiedades para ImageList."""

        label = _("Galería de Avatares")
        icon = "grip"
        template = "expositions/component/avatars_list.html"


class ImageGroupComponent(StructBlock):
    image = ImageChooserBlock(label=_("Imagen"), required=True)
    image_caption = CharBlock(label=_("Pie de imagen"), required=False)
    image_alignment = ChoiceBlock(
        choices=[
            ("left", "A la izquierda"),
            ("right", "A la Derecha"),
            ("full", "Ancho completo"),
        ],
        label=_("Alineación de la imagen"),
        required=True,
        default="left",
    )
    # TODO alinear texto
    rich_text = RichTextBlock(
        label=_("Texto enriquecido"),
        features=[
            "h2",
            "h3",
            "blockquote",
            "underline",
            "bold",
            "italic",
            "superscript",
            "subscript",
            "link",
        ],
    )


class SectionComponent(StructBlock):
    """Componente de Pares Imagen/Texto Enriquecido."""

    show_context_delimiter = BooleanBlock(
        label="Mostrar delimitador de contexto",
        default=True,
        null=True,
        help_text=_("Muestra una línea delimitadora antes de este componente."),
        required=False,
    )
    title = CharBlock(label=_("Título de Sección"), required=False)
    # TODO alinear texto
    intro = RichTextBlock(
        label=_("Texto introductorio"),
        features=[
            "h2",
            "h3",
            "blockquote",
            "underline",
            "bold",
            "italic",
            "superscript",
            "subscript",
            "link",
        ],
        required=False,
    )

    image_group_list = ListBlock(ImageGroupComponent, label=_("Grupos de Imágenes"))

    closure = RichTextBlock(
        label=_("Texto de cierre"),
        features=[
            "h2",
            "h3",
            "blockquote",
            "underline",
            "bold",
            "italic",
            "superscript",
            "subscript",
            "link",
        ],
        required=False,
    )

    class Meta:
        """Meta for SectionComponent."""

        icon = "doc-empty"
        label = _("Lista de Secciones")
        template = "expositions/components/section_list.html"


class ContentTypes(StructBlock):
    block = StaticBlock(
        admin_text=_("Muestra el bloque Tipos de contenido"),
    )

    class Meta:
        icon = "placeholder"
        label = _("Bloque Tipos de contenido")
        template = "expositions/components/content_types.html"


class Expositions(StructBlock):
    block = StaticBlock(
        admin_text=_("Muestra el bloque de exposiciones"),
    )

    class Meta:
        icon = "placeholder"
        label = _("Bloque de exposiciones")
        template = "expositions/components/expositions.html"


class RecommendedElement(StructBlock):
    block = StaticBlock(
        admin_text=_("Muestra el bloque de elementos recomendados"),
    )

    class Meta:
        icon = "placeholder"
        label = _("Bloque de elementos recomendados")
        template = "expositions/components/recommended_element.html"


class MostViewed(StructBlock):
    block = StaticBlock(
        admin_text=_("Lo Más Visto"),
    )

    class Meta:
        icon = "placeholder"
        label = _("Bloque de Lo Más Visto")
        template = "expositions/components/most_viewed.html"


class Allies(StructBlock):
    block = StaticBlock(
        admin_text=_("Muestra el bloque de aliados"),
    )

    class Meta:
        icon = "placeholder"
        label = _("Bloque de aliados")
        template = "expositions/components/allies.html"


class LoggedUser(StaticBlock):
    class Meta:
        icon = "placeholder"
        admin_text = _("Muestra el bloque de usuario logueado")
        label = _("Bloque de usuario logueado")
        template = "expositions/components/logged_user.html"
