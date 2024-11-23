import {
  defaultChoicesUserConfig,
  initChoicesJs
} from "../utils/choices_select_search_filter";
import {
  getCollectionsGroupFormsElement,
  addNewGroupButtonEventsHandlerInit
} from "./searchSelectCollectionsGroups";
import {
  linkCheckboxesWithSelectOptions,
  linkSelectOptionsWithCheckboxes
} from "../utils/linkSelectListAndCheckboxes";

const cardForms = document.querySelectorAll(
  ".ag-js-cardCollectionAddToGroupsForm"
);

cardForms.forEach(cardForm => {
  const {
    choicesWrappers,
    collectionsGroupsSelect,
    collectionsGroupsCheckboxes
  } = getCollectionsGroupFormsElement(cardForm);

  choicesWrappers.forEach(choicesWrapper => {
    initChoicesJs(choicesWrapper, defaultChoicesUserConfig);
  });

  addNewGroupButtonEventsHandlerInit(cardForm);
  linkCheckboxesWithSelectOptions(
    cardForm,
    collectionsGroupsSelect,
    collectionsGroupsCheckboxes
  );
  linkSelectOptionsWithCheckboxes(
    cardForm,
    collectionsGroupsSelect,
    collectionsGroupsCheckboxes
  );
});
