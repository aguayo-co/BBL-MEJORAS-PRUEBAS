"""Define WagTail edit handlers for Resources app."""
from wagtail.admin.panels import MultiFieldPanel


class CollapsibleMultiFieldPanel(MultiFieldPanel):
    """Forced collapsible multifield panel."""

    template = "wagtailadmin/edit_handlers/collapsible_multi_field_panel.html"

    def classes(self):
        """Append required classes to make this collapsible anywhere."""
        classes = super().classes()
        classes.append("collapsible")
        classes.append("object")
        return classes
