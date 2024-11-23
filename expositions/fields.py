from django.utils.translation import gettext_lazy as _
from wagtail.fields import StreamField
from wagtail.snippets.blocks import SnippetChooserBlock

from expositions import editors
from expositions.models.components import (
    Allies,
    AvatarListComponent,
    ContentTypes,
    CustomUserComponent,
    Expositions,
    HelpBlockComponent,
    HeroSliderComponent,
    ImageGroupComponent,
    LinkToContentPagesComponent,
    LoggedUser,
    RecommendedElement,
    MostViewed,
    SectionComponent,
    UserComponent,
)


class FullStreamField(StreamField):
    """Define un campo StreamField con elementos completos."""

    block_types = [
        ("hero_slider_component", HeroSliderComponent()),
        ("help_block_component", HelpBlockComponent()),
        ("user_component", UserComponent()),
        ("custom_user_component", CustomUserComponent()),
        ("avatar_list_component", AvatarListComponent()),
        ("image_group_component", ImageGroupComponent()),
        ("section_component", SectionComponent()),
        ("rich_text", editors.FullEditorBlock()),
        (
            "image_gallery",
            SnippetChooserBlock(
                "expositions.ImageGallery", label=_("Galería de Imágenes")
            ),
        ),
        (
            "video_gallery",
            SnippetChooserBlock(
                "expositions.VideoGallery", label=_("Galería de Vídeos")
            ),
        ),
        ("link_to_content_pages_component", LinkToContentPagesComponent()),
        ("content_types", ContentTypes()),
        ("expositions", Expositions()),
        ("recommended_element", RecommendedElement()),
        ("most_viewed", MostViewed()),
        ("allies", Allies()),
        ("logged_user", LoggedUser()),
    ]

    def __init__(self, **kwargs):
        """Define los campos y bloques a usar e inicializa."""
        super().__init__(block_types=self.block_types, **kwargs)

    def deconstruct(self):
        """Remove positional arguments from deconstruct."""
        name, path, _args, kwargs = super().deconstruct()
        return name, path, [], kwargs


class HeroStreamField(FullStreamField):
    block_types = [
        ("hero_slider_component", HeroSliderComponent()),
    ]


class HomeStreamField(FullStreamField):
    block_types = [
        ("hero_slider_component", HeroSliderComponent()),
        ("help_block_component", HelpBlockComponent()),
        ("link_to_content_pages_component", LinkToContentPagesComponent()),
        ("content_types", ContentTypes()),
        ("expositions", Expositions()),
        ("recommended_element", RecommendedElement()),
        ("most_viewed", MostViewed()),
        ("allies", Allies()),
        ("logged_user", LoggedUser()),
    ]


class ContentStreamField(FullStreamField):
    block_types = [
        ("rich_text", editors.FullEditorBlock()),
        (
            "image_gallery",
            SnippetChooserBlock(
                "expositions.ImageGallery", label=_("Galería de Imágenes")
            ),
        ),
        (
            "video_gallery",
            SnippetChooserBlock(
                "expositions.VideoGallery", label=_("Galería de Vídeos")
            ),
        ),
        ("avatar_list_component", AvatarListComponent()),
        ("section_component", SectionComponent()),
        ("link_to_content_pages_component", LinkToContentPagesComponent()),
    ]


class HelpCenterStreamField(FullStreamField):
    block_types = [
        ("help_block_component", HelpBlockComponent()),
    ]
