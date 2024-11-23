import {
  defaultChoicesUserConfig,
  initChoicesJs
} from "../utils/choices_select_search_filter";
import { getSelectedOptions } from "./select_options_chips";
import {
  getCollectionsGroupFormsElement,
  resetSelectedTagsLinkedWithOptionsChips,
  addNewGroupButtonEventsHandlerInit
} from "./searchSelectCollectionsGroups";
import {
  linkCheckboxesWithSelectOptions,
  linkSelectOptionsWithCheckboxes
} from "../utils/linkSelectListAndCheckboxes";

const editForm = document.forms["collection-form"];

const {
  choicesWrappers,
  collectionsGroupsSelect,
  collectionsGroupsCheckboxes
} = getCollectionsGroupFormsElement(editForm);
choicesWrappers.forEach(choicesWrapper => {
  initChoicesJs(choicesWrapper, defaultChoicesUserConfig);
});

const inputTypes = ["select", "select-multiple"];

getSelectedOptions(editForm, inputTypes).forEach(element => {
  element.addEventListener("change", () =>
    resetSelectedTagsLinkedWithOptionsChips(
      editForm,
      inputTypes,
      collectionsGroupsCheckboxes
    )
  );
});

resetSelectedTagsLinkedWithOptionsChips(
  editForm,
  inputTypes,
  collectionsGroupsCheckboxes
);
addNewGroupButtonEventsHandlerInit(editForm, true, inputTypes);
linkCheckboxesWithSelectOptions(
  editForm,
  collectionsGroupsSelect,
  collectionsGroupsCheckboxes,
  true,
  inputTypes
);
linkSelectOptionsWithCheckboxes(
  editForm,
  collectionsGroupsSelect,
  collectionsGroupsCheckboxes
);
