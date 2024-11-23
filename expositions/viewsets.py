"""Module to custom selectors (choosers) viewsets."""
from wagtail.admin.views.generic.chooser import ChooseView, ChooseResultsView
from wagtail.admin.viewsets.chooser import ChooserViewSet


class ResourceChooseChooseViewClass(ChooseView):
    """Limits the resource list for a chooser."""
    def get_object_list(self):
        return self.model_class.objects.filter(visible=True, setandresource__isnull=False)


class ResourceChooseResultsView(ChooseResultsView):
    """Limits the equivalence list for a chooser to only SubjectEquivalence."""

    def get_object_list(self):
        return self.model_class.objects.filter(visible=True, setandresource__isnull=False)


class TypeEquivalenceChooseViewClass(ChooseView):
    """Limits the equivalence list for a chooser to only TypeEquivalence."""
    def get_object_list(self):
        return self.model_class.objects.filter(field="type")


class TypeEquivalenceChooseResultsView(ChooseResultsView):
    """Limits the equivalence list for a chooser to only SubjectEquivalence."""

    def get_object_list(self):
        return self.model_class.objects.filter(field="type")


class SubjectEquivalenceChooseViewClass(ChooseView):
    """Limits the equivalence list for a chooser to only SubjectEquivalence."""

    def get_object_list(self):
        return self.model_class.objects.filter(field="subject")


class SubjectEquivalenceChooseResultsView(ChooseResultsView):
    """Limits the equivalence list for a chooser to only SubjectEquivalence."""

    def get_object_list(self):
        return self.model_class.objects.filter(field="subject")


class ResourceChooserViewSet(ChooserViewSet):
    """Custom selector chooser for Resources."""
    model = "harvester.ContentResource"
    choose_one_text = "Seleccione un Recurso"
    choose_another_text = "Seleccione otro Recurso"
    edit_item_text = "Editar este Recurso"
    icon = "doc-full-inverse"
    choose_view_class = ResourceChooseChooseViewClass
    choose_results_view_class = ResourceChooseResultsView


class TypeEquivalenceChooserViewSet(ChooserViewSet):
    """Custom selector chooser for TypeEquivalences."""
    model = "harvester.Equivalence"
    choose_one_text = "Seleccione un Tipo de Contenido"
    choose_another_text = "Seleccione otro Tipo de Contenido"
    edit_item_text = "Editar este Tipo de Contenido"
    icon = "clipboard-list"
    choose_view_class = TypeEquivalenceChooseViewClass
    choose_results_view_class = TypeEquivalenceChooseResultsView


class SubjectEquivalenceChooserViewSet(ChooserViewSet):
    """Custom selector chooser for SubjectEquivalences."""
    model = "harvester.SubjectEquivalence"
    choose_one_text = "Seleccione un Tema"
    choose_another_text = "Seleccione otro Tema"
    edit_item_text = "Editar este Tema"
    icon = "clipboard-list"
    choose_view_class = SubjectEquivalenceChooseViewClass
    choose_results_view_class = SubjectEquivalenceChooseResultsView


class UserChooserViewSet(ChooserViewSet):
    """Custom selector chooser for Users."""
    model = "custom_user.User"
    choose_one_text = "Seleccione un Usuario"
    choose_another_text = "Seleccione otro Usuario"
    edit_item_text = "Editar este Usuario"
    icon = "clipboard-list"


content_resource_viewset = ResourceChooserViewSet("resource_chooser")
type_equivalence_viewset = TypeEquivalenceChooserViewSet("type_equivalence_chooser")
subject_equivalence_viewset = SubjectEquivalenceChooserViewSet("subject_equivalence_chooser")
user_viewset = UserChooserViewSet("user_chooser")
