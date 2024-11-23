"""Edit Handlers for Wagtail Admin."""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import InlinePanel, ObjectList
from wagtail.embeds import embeds
from wagtail.embeds.blocks import EmbedBlock


class LimitedEmbedMixin:
    """Mixin to limit providers on an embed block."""

    ALLOWED_PROVIDERS = []
    INVALID_PROVIDER_ERROR = _(
        "%(provider)s no es una fuente permitida. Se permiten urls de las"
        " siguientes fuentes: %(providers)s."
    )

    def __init__(self, *args, **kwargs):
        """Extend default init to set _allowed_providers property."""
        super().__init__(*args, **kwargs)
        self._allowed_providers = [
            provider.lower() for provider in self.ALLOWED_PROVIDERS
        ]

    def clean(self, value):
        """Extend validation to check for allowed providers."""
        value = super().clean(value)
        if value:
            # By now we have a valid embed.
            embed = embeds.get_embed(value.url)
            if embed.provider_name.lower() not in self._allowed_providers:
                raise ValidationError(
                    self.INVALID_PROVIDER_ERROR
                    % {
                        "provider": embed.provider_name,
                        "providers": ", ".join(self.ALLOWED_PROVIDERS),
                    }
                )
        return value


class VideoBlock(EmbedBlock):
    """Bloque embed que limita a videos."""
    pass


class MapMilestoneInlineCreator(InlinePanel):
    """Custom Inline Creator for Milestones."""

    template = "wagtailadmin/edit_handlers/map_milestone_creator_panel.html"


class TimelineMilestoneInlineCreator(InlinePanel):
    """Custom Inline Creator for Milestones in Timeline."""

    template = "wagtailadmin/edit_handlers/timeline_milestone_creator_panel.html"


class FixedObjectList(ObjectList):
    """Object List With Fixed Elements"""

    hide_on_add = None

    def __init__(self, *args, **kwargs):
        """Init the fixed edithandler and set custom properties."""
        self.hide_on_add = kwargs.pop("hide_on_add", None)
        super().__init__(*args, **kwargs)

    def clone_kwargs(self):
        """Clone the kwargs and set custom kwargs."""
        kwargs = super().clone_kwargs()
        kwargs["hide_on_add"] = self.hide_on_add
        return kwargs

    def bind_to(self, model=None, instance=None, request=None, form=None):
        self.request = self.request if request is None else request
        return super().bind_to(
            model=model, instance=instance, request=request, form=form
        )

    def on_request_bound(self):
        """Bind The Request and hide panels by related_name or field_name."""
        if (
            self.request.resolver_match.url_name == "add"
            or self.request.method == "POST"
        ) and self.hide_on_add:
            self.children = [
                child
                for child in self.children
                if not getattr(child, "field_name", None) in self.hide_on_add
                and not getattr(child, "relation_name", None) in self.hide_on_add
            ]
        super().on_request_bound()
