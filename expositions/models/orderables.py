"""intermediate models to link models as sortables."""
from django.db import models
from django.db.models import ForeignKey
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    PageChooserPanel,
)
from wagtail.models import Orderable


class ThemePageSidebarItem(Orderable):

    sidebar = ParentalKey(
        "expositions.Sidebar",
        related_name="related_themes",
    )
    theme = ForeignKey(
        "expositions.ThemePage",
        verbose_name="Tema",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True
    )

    panels = [
        PageChooserPanel("theme"),
    ]

class QuestionPageSidebarItem(Orderable):

    sidebar = ParentalKey(
        "expositions.Sidebar",
        related_name="related_question",
    )
    question = ForeignKey(
        "expositions.QuestionPage",
        verbose_name="Pregunta",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True
    )

    panels = [
        PageChooserPanel("question"),
    ]
