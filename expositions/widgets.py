"""Custom Widgets for Wagtail Admin."""
from instance_selector.selectors import ModelAdminInstanceSelector

from expositions.models.admin import (
    ContentResourceWagtailAdmin,
    UserWagtailAdmin,
    TypeEquivalenceWagtailAdmin,
)


class BaseSelector(ModelAdminInstanceSelector):
    """Reusable an Instance Selector."""

    editable = False

    def get_instance_display_markup(self, instance):
        """Override the selected element title."""
        if instance:
            if self.editable:
                return super().get_instance_display_markup(instance)
            return instance.__str__()
        return ""


class ContentResourceSelector(BaseSelector):
    """Create an Instance Selector for Content Resource."""

    model_admin = ContentResourceWagtailAdmin()


class UserSelector(BaseSelector):
    """Create an Instance Selector for User."""

    model_admin = UserWagtailAdmin()


class TypeEquivalenceSelector(BaseSelector):
    """Create an Instance Selector for Type Equivalence."""

    model_admin = TypeEquivalenceWagtailAdmin()
