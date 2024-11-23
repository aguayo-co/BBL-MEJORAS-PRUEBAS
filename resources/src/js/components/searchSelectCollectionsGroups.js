import { resetSelectedOptionsTags } from "./select_options_chips";
import { addNewSelectedOption } from "../utils/choices_select_search_filter";

export function getCollectionsGroupFormsElementClassNames() {
  return {
    selectChoicesJsWrapperClassName: "ag-js-choices-collections-group",
    checkboxChoicesJsWrapperClassName: "ag-js-checkboxes-collections-group",
    addNewGroupInputsClassName: "ag-js-newCollectionsGroupName",
    addNewGroupButtonsClassName: "ag-js-addNewCollectionsGroup"
  };
}

export function getCollectionsGroupFormsElement(scope = document) {
  const {
    selectChoicesJsWrapperClassName,
    checkboxChoicesJsWrapperClassName,
    addNewGroupInputsClassName,
    addNewGroupButtonsClassName
  } = getCollectionsGroupFormsElementClassNames();
  return {
    choicesWrappers: scope.querySelectorAll(
      `.${selectChoicesJsWrapperClassName}`
    ),
    addNewGroupInputs: scope.querySelectorAll(`.${addNewGroupInputsClassName}`),
    addNewGroupButtons: scope.querySelectorAll(
      `.${addNewGroupButtonsClassName}`
    ),
    collectionsGroupsSelect: scope.querySelector(
      `.${selectChoicesJsWrapperClassName} select`
    ),
    collectionsGroupsCheckboxes: scope.querySelectorAll(
      `.${checkboxChoicesJsWrapperClassName} input[type="checkbox"]`
    )
  };
}

export function linkSelectedOptionsChipsWithCheckboxes(
  form = document,
  checkboxes
) {
  form.querySelectorAll(".ag-js-filterTag").forEach(tag => {
    tag.addEventListener("click", () => {
      const textContent = tag.querySelector(".ag-filter-chip__text")
        .textContent;
      const linkedCheckbox = Array.from(checkboxes).find(checkbox =>
        Array.from(checkbox.labels).some(
          label => label.textContent === textContent
        )
      );
      if (linkedCheckbox) {
        linkedCheckbox.checked = false;
      }
    });
  });
}

export function resetSelectedTagsLinkedWithOptionsChips(
  form,
  inputTypes,
  checkboxes
) {
  resetSelectedOptionsTags(form, inputTypes);
  linkSelectedOptionsChipsWithCheckboxes(form, checkboxes);
}

export function addNewGroupButtonEventsHandlerInit(
  form,
  usingFilterChips = false,
  inputTypesForFilterChips = null
) {
  const {
    collectionsGroupsSelect,
    collectionsGroupsCheckboxes,
    addNewGroupInputs,
    addNewGroupButtons
  } = getCollectionsGroupFormsElement(form);
  if (addNewGroupInputs.length && addNewGroupButtons.length) {
    const {
      addNewGroupInputsClassName
    } = getCollectionsGroupFormsElementClassNames();
    addNewGroupButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        const addNewGroupInput = btn.parentElement.querySelector(
          `.${addNewGroupInputsClassName}`
        );
        if (addNewGroupInput && addNewGroupInput.value) {
          addNewSelectedOption(
            addNewGroupInput.value,
            null,
            collectionsGroupsSelect.id
          );
          addNewGroupInput.value = "";
          if (usingFilterChips) {
            resetSelectedTagsLinkedWithOptionsChips(
              form,
              inputTypesForFilterChips,
              collectionsGroupsCheckboxes
            );
          }
        }
      });
    });
  }
}
