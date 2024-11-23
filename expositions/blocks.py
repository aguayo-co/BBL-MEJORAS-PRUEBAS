"""Module for custom selectors (choosers) blocks."""
from expositions.viewsets import content_resource_viewset, type_equivalence_viewset, subject_equivalence_viewset, \
    user_viewset

ResourceChooserBlock = content_resource_viewset.get_block_class(
    name="ResourceChooserBlock", module_path="expositions.blocks"
)

TypeEquivalenceChooserBlock = type_equivalence_viewset.get_block_class(
    name="TypeEquivalenceChooserBlock", module_path="expositions.blocks"
)

SubjectEquivalenceChooserBlock = subject_equivalence_viewset.get_block_class(
    name="SubjectEquivalenceChooserBlock", module_path="expositions.blocks"
)

UserChooserBlock = user_viewset.get_block_class(
    name="UserChooserBlock", module_path="expositions.blocks"
)
