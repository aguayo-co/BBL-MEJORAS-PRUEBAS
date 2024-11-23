from django_select2.forms import ModelSelect2Widget


class SetAutocompleteWidget(ModelSelect2Widget):
    search_fields = [
        "name__icontains",
        "spec__icontains",
    ]


class SubjectAutocompleteWidget(ModelSelect2Widget):
    search_fields = [
        "name__icontains",
    ]
