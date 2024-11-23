from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.models import Orderable, Page
from wagtailmenus.models import (
    AbstractFlatMenuItem,
    AbstractMainMenu,
    AbstractMainMenuItem,
    FlatMenuItem,
)


class AGFlatMenuItem(AbstractFlatMenuItem):
    """A custom menu item model to be used by ``wagtailmenus.MainMenu``"""

    menu = ParentalKey(
        "wagtailmenus.FlatMenu",
        on_delete=models.CASCADE,
        related_name="custom_flat_menu_items",
    )
