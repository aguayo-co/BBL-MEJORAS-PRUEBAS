"""Define models for WagTail pages for expositions app."""

from datetime import timedelta

from constance import config
from django import forms
from django.core import validators
from django.core.paginator import Paginator
from django.core.validators import ValidationError
from django.db import models
from django.db.models import Count
from django.forms import CheckboxInput
from django.http import HttpResponsePermanentRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
    TitleFieldPanel,
)
from wagtail.admin.widgets.slug import SlugInput
from wagtail.blocks import PageChooserBlock, StreamBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail.snippets.blocks import SnippetChooserBlock
from biblored.settings import WAGTAIL_APPEND_SLASH
from expositions import editors
from expositions.fields import (
    ContentStreamField,
    HelpCenterStreamField,
    HeroStreamField,
    HomeStreamField,
)
from expositions.models.components import (
    AvatarListComponent,
    LinkToContentPagesComponent,
    SectionComponent,
)
from harvester.models import (
    Collection,
    ContentResource,
    DataSource,
    PromotedContentResource,
    Set,
)
from resources.validators import HtmlMaxLengthValidator

CONTENT_BLOCKS = [
    ("rich_text", editors.FullEditorBlock()),
    (
        "image_gallery",
        SnippetChooserBlock("expositions.ImageGallery", label=_("Galería de Imágenes")),
    ),
    (
        "video_gallery",
        SnippetChooserBlock("expositions.VideoGallery", label=_("Galería de Vídeos")),
    ),
    ("map", SnippetChooserBlock("expositions.Map", label=_("Mapa"))),
    ("cloud", SnippetChooserBlock("expositions.Cloud", label=_("Nube de Términos"))),
    (
        "timeline",
        SnippetChooserBlock("expositions.Timeline", label=_("Línea de Tiempo")),
    ),
    ("narrative", SnippetChooserBlock("expositions.Narrative", label=_("Narrativa"))),
    ("avatar_list", AvatarListComponent()),
    ("section_list", SectionComponent()),
    ("link_to_content_pages", LinkToContentPagesComponent()),
]


class AbstractExpositionPage(Page, index.Indexed):
    """Abstract page for all WagTail pages for Expositions app."""

    show_in_menus_default = True
    search_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Imagen para buscadores."),
    )
    keywords = models.CharField(
        default="", blank=True, max_length=100, verbose_name=_("Palabras clave")
    )
    search_fields = [
        index.SearchField("title", partial_match=True, boost=2),
        index.AutocompleteField("title"),
        index.FilterField("title"),
    ]

    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel("slug", widget=SlugInput),
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
                FieldPanel("keywords"),
                FieldPanel("search_image"),
            ],
            heading=_("Para motores de búsqueda"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("show_in_menus"),
            ],
            heading=_("Para menús del sitio"),
        ),
    ]

    def get_url_parts(self, request=None):
        """Override original `Page.get_url_parts` method to use custom named route."""
        possible_sites = [
            (pk, path, url, lang_code)
            for pk, path, url, lang_code in self._get_site_root_paths(request)
            if self.url_path.startswith(path)
        ]

        if not possible_sites:
            return None

        site_id, root_path, root_url, lang_code = possible_sites[0]

        if hasattr(request, "site"):
            for site_id, _root_path, _root_url, _lang_code in possible_sites:
                if site_id == request.site.pk:
                    break
            else:
                site_id, root_path, root_url, lang_code = possible_sites[0]

        page_path = reverse(
            "expositions:wagtail_serve", args=(self.url_path[len(root_path) :],)
        )

        # Remove the trailing slash from the URL reverse generates if
        # WAGTAIL_APPEND_SLASH is False and we're not trying to serve
        # the root path
        if not WAGTAIL_APPEND_SLASH and page_path != "/":
            page_path = page_path.rstrip("/")

        return (site_id, root_url, page_path)

    class Meta:
        """Define properties for AbstractExpositionPage models."""

        abstract = True


class Exposition(AbstractExpositionPage):
    """Define an Exposition container."""

    TEXT_TAGS = ["bold", "italic"]

    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("Imagen"),
    )
    description = RichTextField(
        features=TEXT_TAGS,
        validators=[HtmlMaxLengthValidator(300)],
        verbose_name=_("Descripción"),
        max_length=320,
    )
    author = models.ForeignKey(
        "custom_user.User", on_delete=models.PROTECT, verbose_name=_("Autor")
    )

    sub_title = models.CharField(
        max_length=255, blank=True, verbose_name=_("Subtítulo")
    )
    intro = RichTextField(
        features=TEXT_TAGS,
        validators=[HtmlMaxLengthValidator(150)],
        blank=True,
        verbose_name=_("Introducción"),
        max_length=170,
    )
    subject = models.ForeignKey(
        "harvester.SubjectEquivalence",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        verbose_name=_("Tema"),
    )
    theme = models.TextField(
        choices=(
            ("magenta", _("Magenta")),
            ("purple", _("Púrpura")),
            ("blue", _("Azul")),
        ),
        default="magenta",
        verbose_name=_("Color de la Plantilla"),
        help_text=_(
            "Personaliza la apariencia de la exposición cambiando el color del tema."
        ),
    )
    exposition_type = models.ForeignKey(
        "expositions.TypeExposition",
        verbose_name=_("Tipo de exposición"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    related_expositions = StreamField(
        StreamBlock(
            [
                (
                    "exposition",
                    PageChooserBlock(
                        "expositions.Exposition",
                        label=_("Exposición"),
                        max_num=4,
                        icon="form",
                    ),
                )
            ],
            max_num=4,
            min_num=0,
            required=False,
        ),
        verbose_name="Exposiciones Relacionadas",
        blank=True,
        null=True,
        use_json_field=True,
    )

    promoted_section = models.BooleanField(
        verbose_name=_("promover en sección"),
        default=False,
        help_text=_("Muestra la Exposición en el home de exposiciones."),
    )
    promoted_site = models.BooleanField(
        verbose_name=_("promover en el home"),
        default=False,
        help_text=_("Muestra la Exposición en el home principal del sitio."),
    )

    content_panels = [
        MultiFieldPanel(
            [
                TitleFieldPanel("title"),
                FieldPanel("image"),
                FieldPanel("exposition_type"),
                FieldPanel("theme", widget=forms.Select),
                FieldPanel("description"),
            ],
            _("Definición"),
        ),
        MultiFieldPanel(
            [FieldPanel("sub_title"), FieldPanel("intro")], _("Introducción")
        ),
        MultiFieldPanel(
            [
                FieldPanel("subject"),
                FieldPanel("author"),
                FieldPanel("related_expositions"),
            ],
            _("Otra información"),
        ),
    ]

    promote_panels = AbstractExpositionPage.promote_panels + [
        FieldPanel("promoted_section"),
        FieldPanel("promoted_site"),
    ]

    parent_page_types = [
        "wagtailcore.Page",
        "expositions.Redirection",
        "expositions.HomePage",
    ]
    subpage_types = [
        "expositions.ExpositionSection",
        "expositions.Redirection",
    ]

    search_fields = Page.search_fields + [
        index.SearchField("title", partial_match=True),
        index.SearchField("sub_title", partial_match=True),
    ]

    def validate_max_promoted(self, field, max_promoted):
        """
        Validate that no more than `max_promoted` instances are promoted for `field`.

        If data is not valid, return an instance of `ValidationError`.
        """
        if not getattr(self, field):
            return None

        promoted__count = (
            self.__class__.objects.live().filter(**{field: 1}).not_page(self).count()
        )
        if promoted__count < max_promoted:
            return None

        msg = _(
            "Máximo %(max)d Exposiciones se pueden promover."
            " Para promover esta debes dejar de promover una de las actuales."
        )
        return ValidationError(msg, params={"max": max_promoted})

    def clean(self):
        """Perform custom validations for Expositions."""
        errors = {}

        promoted_site_errors = self.validate_max_promoted("promoted_site", 3)
        if promoted_site_errors:
            errors["promoted_site"] = promoted_site_errors

        promoted_section_errors = self.validate_max_promoted("promoted_section", 3)
        if promoted_section_errors:
            errors["promoted_section"] = promoted_section_errors

        if errors:
            raise ValidationError(errors)

    def get_absolute_url(self):
        """Workaround to build_absolute_uri."""
        return self.url

    class Meta:
        """Meta exposition class."""

        verbose_name = _("exposición")
        verbose_name_plural = _("exposiciones")
        app_label = "expositions"


class AbstractExpositionSection(AbstractExpositionPage):
    """Define common properties for all Exposition setcions."""

    parent_page_types = ["expositions.Exposition"]
    subpage_types = []

    class Meta:
        """Define properties for AbstractExpositionSection models."""

        abstract = True

    def get_exposition(self):
        """Return the Exposition for this section."""
        return self.get_ancestors().type(Exposition).first()


class ExpositionSection(AbstractExpositionSection):
    """Define an Exposition section or page."""

    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("Imagen"),
    )
    short_description = models.TextField(
        max_length=200, verbose_name=_("Descripción Corta")
    )
    long_description = models.TextField(verbose_name=_("Descripción Larga"))
    subject = models.ForeignKey(
        "harvester.SubjectEquivalence",
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to={"field": "subject"},
        null=True,
        verbose_name=_("Tema"),
    )
    rich_text_title = models.TextField(
        max_length=150,
        verbose_name=_("Titulo de Texto Enriquecido"),
        help_text=_(
            "Encabezado que se muestra si la sección de contenido inicia con un texto enriquecido."
        ),
        blank=True,
        null=True,
    )
    show_context_delimiter = models.BooleanField(
        default=True,
        null=True,
        verbose_name=_("Mostrar delimitador de Contexto"),
    )
    rich_text_intro = models.TextField(
        max_length=200,
        verbose_name=_("Introducción de Texto Enriquecido"),
        help_text=_(
            "Introducción corta que se muestra si la sección de contenido inicia con un texto enriquecido."
        ),
        blank=True,
        null=True,
    )
    content = StreamField(CONTENT_BLOCKS, verbose_name="Contenido", use_json_field=True)

    related_expositions = StreamField(
        StreamBlock(
            [
                (
                    "exposition",
                    PageChooserBlock(
                        "expositions.exposition",
                        label=_("Exposición"),
                        max_num=4,
                        icon="form",
                    ),
                )
            ],
            max_num=4,
            min_num=0,
            required=False,
        ),
        verbose_name="Exposiciones Relacionadas",
        blank=True,
        null=True,
        use_json_field=True,
    )

    content_panels = [
        MultiFieldPanel(
            [
                TitleFieldPanel("title"),
                FieldPanel("image"),
                FieldPanel("short_description"),
                FieldPanel("long_description"),
                FieldPanel("subject"),
                FieldPanel("related_expositions"),
            ],
            _("Definición"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("show_context_delimiter", widget=CheckboxInput),
                FieldPanel("rich_text_title"),
                FieldPanel("rich_text_intro"),
            ],
            _("Texto Enriquecido"),
        ),
        FieldPanel("content"),
    ]
    search_fields = []

    class Meta:
        """Meta exposition class."""

        verbose_name = _("Sección de exposición")
        verbose_name_plural = _("Secciones de exposición")
        app_label = "expositions"


class Redirection(AbstractExpositionSection):
    """Define an Exposition section that acts as a redirect."""

    redirect_url = models.URLField(
        validators=[validators.URLValidator(schemes=["http", "https"])],
        help_text=_(
            "La URL a la cual el usuario será redirigido. Ejemplo:"
            " https://www.example.com/ruta-al-documento"
        ),
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.PROTECT,
        related_name="+",
        blank=True,
        null=True,
    )

    preview_modes = []

    content_panels = [
        MultiFieldPanel(
            [
                TitleFieldPanel("title"),
                FieldPanel("redirect_url"),
                # ImageChooserPanel("image"),
            ],
            _("Definición"),
        )
    ]
    parent_page_types = [
        "wagtailcore.Page",
        "expositions.Redirection",
        "expositions.HomePage",
    ]
    subpage_types = [
        "expositions.Redirection",
        "expositions.Exposition",
        "expositions.ContentPage",
    ]

    def serve(self, request, *args, **kwargs):
        """Serve a redirection to the defined url."""
        request.is_preview = getattr(request, "is_preview", False)

        return HttpResponsePermanentRedirect(self.redirect_url)

    @property
    def url(self):
        """Returns the URL for pageurl templatetag."""
        return self.redirect_url

    def relative_url(self, current_site, request=None):
        """Returns the relative URL if exists."""
        return self.redirect_url


class ContentPage(AbstractExpositionSection):
    content = ContentStreamField(
        verbose_name=_("Contenido"), blank=True, null=True, use_json_field=True
    )

    content_panels = [
        TitleFieldPanel("title"),
        FieldPanel("content"),
    ]
    parent_page_types = [
        "expositions.HomePage",
        "expositions.Redirection",
        "expositions.ContentPage",
    ]
    subpage_types = ["expositions.ContentPage"]

    class Meta:
        verbose_name = _("Página de contenido")
        verbose_name_plural = _("Páginas de contenido")


class HelpCenterPage(AbstractExpositionSection):
    parent_page_types = [
        "expositions.HomePage",
    ]

    max_count_per_parent = 1
    description = models.TextField(
        max_length=400,
        verbose_name=_("Descripción"),
        blank=True,
        null=True,
    )

    content = HelpCenterStreamField(
        verbose_name=_("Contenido"), blank=True, null=True, use_json_field=True
    )

    content_panels = [
        MultiFieldPanel(
            [
                TitleFieldPanel("title"),
                FieldPanel("description"),
            ],
            _("Definición"),
        ),
        FieldPanel("content"),
    ]

    subpage_types = ["expositions.ThemePage"]

    def get_context(self, request):
        context = super().get_context(request)
        help_center_themes = []

        # Get theme´s live current questions
        for theme in self.get_children().live():
            process_data_help_center_themes = {
                "theme": theme,
                "questions_theme": theme.get_children().live(),
            }
            help_center_themes.append(process_data_help_center_themes)

        context["help_center_themes"] = help_center_themes
        return context

    class Meta:
        verbose_name = _("Página de Centro de Ayuda")
        verbose_name_plural = _("Páginas de Centro de Ayuda")


class ThemePage(AbstractExpositionSection):
    """Model for themes on help center."""

    description = models.TextField(null=True, blank=True, verbose_name=_("Descripción"))
    content = ContentStreamField(
        verbose_name=_("Contenido"), blank=True, null=True, use_json_field=True
    )

    content_panels = [
        MultiFieldPanel([TitleFieldPanel("title"), FieldPanel("description")]),
        FieldPanel("content"),
    ]
    parent_page_types = [
        "expositions.HelpCenterPage",
    ]
    subpage_types = ["expositions.QuestionPage"]

    ordering_options = {
        "az": (_("De la a A a la Z"), ["title"]),
        "za": (_("De la Z a la A"), ["-title"]),
        "recent": (_("Más reciente"), ["-last_published_at"]),
        "-recent": (_("Menos reciente"), ["last_published_at"]),
    }
    default_ordering = None

    def order_queryset(self, queryset):
        """Apply ordering and return the ordered queryset."""
        ordering = self.get_ordering()
        if ordering:
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_ordering(self):
        """Return the field or fields to use for ordering the queryset."""
        applied_ordering = self.get_applied_ordering()
        if applied_ordering:
            return self.ordering_options[applied_ordering][1]

    def get_applied_ordering(self):
        """Return the order_by option to use."""
        order_by = self.request.GET.get("order_by")
        if order_by in self.ordering_options:
            return order_by
        return None

    def get_context(self, request):
        self.request = request
        context = super().get_context(request)

        # Get Page
        current_page = context["request"].GET.get("page", 1)

        # Only promoted questions
        context["promoted_questions"] = (
            QuestionPage.objects.live()
            .descendant_of(self)
            .filter(promoted_section=True)
            .order_by("-last_published_at")
        )

        # Child Pages Paginated and ordered
        queryset = self.order_queryset(QuestionPage.objects.live().descendant_of(self))
        object_list = QuestionPage.objects.live().descendant_of(self)
        paginator = Paginator(queryset, config.PAGE_SIZE)

        context.update(
            {
                "paginator": paginator,
                "page_obj": paginator.get_page(current_page),
                "is_paginated": paginator.num_pages > 1,
                "object_list": object_list or [],
                "ordering_options": {
                    key: options[0] for key, options in self.ordering_options.items()
                },
                "applied_ordering": self.get_applied_ordering(),
            }
        )
        return context

    class Meta:
        verbose_name = _("Página de Tema")
        verbose_name_plural = _("Páginas de Tema")


class QuestionPage(AbstractExpositionSection):
    parent_page_types = [
        "expositions.ThemePage",
    ]

    description = models.TextField(null=True, blank=True, verbose_name=_("Descripción"))
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        verbose_name=_("Imagen"),
    )
    promoted_section = models.BooleanField(
        default=False,
        verbose_name=_("promover en sección"),
        help_text=_("Destaca la Pregunta en el home de Tema."),
    )
    content = ContentStreamField(
        verbose_name=_("Contenido"), blank=True, null=True, use_json_field=True
    )
    sidebar = models.ForeignKey(
        "expositions.Sidebar",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Sidebar"),
    )

    footer_content = ContentStreamField(
        verbose_name=_("Contenido Footer"), blank=True, null=True, use_json_field=True
    )

    promote_panels = AbstractExpositionSection.promote_panels

    settings_panels = AbstractExpositionSection.settings_panels

    content_panels = [
        MultiFieldPanel(
            [
                TitleFieldPanel("title"),
                FieldPanel("description"),
                FieldPanel("image"),
                FieldPanel("promoted_section"),
            ],
            _("Definición"),
        ),
        FieldPanel("content"),
        FieldPanel("footer_content"),
    ]

    sidebar_panels = [
        MultiFieldPanel(
            [
                FieldPanel("sidebar"),
            ],
            heading=_("Sidebar"),
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading=_("Contenido")),
            ObjectList(sidebar_panels, heading=_("Sidebar")),
            ObjectList(promote_panels, heading=_("Promocionar")),
            ObjectList(settings_panels, heading=_("Ajustes")),
        ]
    )

    subpage_types = []

    class Meta:
        verbose_name = _("Página de Pregunta")
        verbose_name_plural = _("Páginas de Pregunta")


class HomePage(AbstractExpositionSection):
    parent_page_types = ["wagtailcore.Page"]

    hero = HeroStreamField(
        verbose_name=_("Banner Hero"), blank=True, null=True, use_json_field=True
    )
    content = HomeStreamField(
        verbose_name=_("Contenido"), blank=True, null=True, use_json_field=True
    )
    __collections = None
    __most_read = None
    __based_on_reads = None

    content_panels = [
        TitleFieldPanel("title"),
        FieldPanel("hero"),
        FieldPanel("content"),
    ]

    subpage_types = [
        "expositions.Exposition",
        "expositions.Redirection",
        "expositions.HelpCenterPage",
        "expositions.ContentPage",
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        if request.user.is_authenticated:
            context["based_on_reads"] = list(self.get_based_on_reads(request))
        context["most_read"] = list(self.get_most_read)
        context["collections"] = self.collections
        context["expositions"] = list(self.get_expositions())
        context["curated_collections"] = list(self.get_curated_collections())
        context["promoted_resources"] = list(self.get_promoted_resources())
        context["allies"] = list(self.get_allies())
        return context

    @property
    def collections(self):
        if self.__collections is None:
            queryset = (
                Collection.objects.annotate_groups()
                .visible()
                .prefetch_related("collaborativecollection")
                .exclude(
                    # Exclude Subchildren
                    Collection.objects.get_subclasses_excludes(),
                    # Only if are not CollaborativeCollection
                    collaborativecollection__isnull=True,
                )
                .filter(public=True, home_site=True)
                .all()[:4]
            )
            collections = []
            for collection in queryset:
                collections.append(
                    getattr(collection, "collaborativecollection", collection)
                )
            self.__collections = collections
        return self.__collections

    def get_based_on_reads(self, request=None):
        """Return a list of the Based on Your Reads ContentResources."""
        if self.__based_on_reads is None:
            self.__based_on_reads = (
                ContentResource.objects.filter(hitcount__hit__user=request.user)
                .annotate(hits=Count("hitcount__hit"))
                .visible()
                .order_by("-hits", "data_source__relevance")[:2]
            )
        return self.__based_on_reads

    @property
    def get_most_read(self):
        """
        Return queryset for most popular ContentResource by collection count.

        Only include resources that have been added to a collection in the last 7 days.
        """
        seven_days_ago = timezone.now() + timedelta(days=-7)
        if self.__most_read is None:
            self.__most_read = (
                ContentResource.objects.visible()
                .filter(
                    data_source__online_resources=True,
                    collectionandresource__isnull=False,
                )
                .annotate(Count("collectionandresource"))
                .filter(collectionandresource__created_at__gt=seven_days_ago)
                .order_by("-collectionandresource__count")[:6]
            )

        return self.__most_read

    @staticmethod
    def get_curated_collections():
        """Return a list of Sets selected by admins."""
        return Set.objects.visible().filter(home_site=True)[:4]

    @staticmethod
    def get_expositions():
        """Return a list of promoted Exposition."""
        return Exposition.objects.live().filter(promoted_site=True)

    @staticmethod
    def get_allies():
        """Return a list of DataSources marked as allied."""
        return DataSource.objects.filter(is_ally=True)

    @staticmethod
    def get_promoted_resources():
        """Return a list of PromotedContentResource."""
        return PromotedContentResource.objects.visible()
