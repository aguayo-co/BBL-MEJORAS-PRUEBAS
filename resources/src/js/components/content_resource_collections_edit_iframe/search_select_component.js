import {
  defaultChoicesUserConfig,
  initChoicesJs
} from "../../utils/choices_select_search_filter";
import {
  linkCheckboxesWithSelectOptions,
  linkSelectOptionsWithCheckboxes
} from "../../utils/linkSelectListAndCheckboxes";

const editForm = document.forms["content-resource-collections-edit-form"];

if (editForm) {
  const choicesWrappers = editForm.querySelectorAll(
    ".ag-js-choices-collections-select"
  );
  const collectionsSelect = editForm.querySelector(
    ".ag-js-choices-collections-select select"
  );
  const collectionsCheckboxes = editForm.querySelectorAll(
    '.ag-js-choices-collections-checkboxes input[type="checkbox"]'
  );
  choicesWrappers.forEach(choicesWrapper => {
    initChoicesJs(choicesWrapper, defaultChoicesUserConfig);
  });

  linkCheckboxesWithSelectOptions(
    editForm,
    collectionsSelect,
    collectionsCheckboxes
  );
  linkSelectOptionsWithCheckboxes(
    editForm,
    collectionsSelect,
    collectionsCheckboxes
  );
}
