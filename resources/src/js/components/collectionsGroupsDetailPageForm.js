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

const detailForm = document.forms["collection-detail-form"];
const {
  choicesWrappers,
  collectionsGroupsSelect,
  collectionsGroupsCheckboxes
} = getCollectionsGroupFormsElement(detailForm);

choicesWrappers.forEach(choicesWrapper => {
  initChoicesJs(choicesWrapper, defaultChoicesUserConfig);
});

addNewGroupButtonEventsHandlerInit(detailForm);
linkCheckboxesWithSelectOptions(
  detailForm,
  collectionsGroupsSelect,
  collectionsGroupsCheckboxes
);
linkSelectOptionsWithCheckboxes(
  detailForm,
  collectionsGroupsSelect,
  collectionsGroupsCheckboxes
);
