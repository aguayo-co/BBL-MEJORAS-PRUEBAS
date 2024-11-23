import {
  defaultChoicesUserConfig,
  initChoicesJs
} from "../utils/choices_select_search_filter";

const choicesWrappers = document.querySelectorAll(".ag-js-choices");

choicesWrappers.forEach(choicesWrapper => {
  initChoicesJs(choicesWrapper, defaultChoicesUserConfig);
});
