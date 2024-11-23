import { clearSelectedOption } from "../components/select_options_chips";
import { resetSelectedTagsLinkedWithOptionsChips } from "../components/searchSelectCollectionsGroups";
import { addNewSelectedOption } from "./choices_select_search_filter";

export function linkCheckboxesWithSelectOptions(
  form,
  select,
  checkboxes,
  usingOptionsChips = false,
  inputTypesForOptionsChips = null
) {
  checkboxes.forEach(checkbox => {
    checkbox.addEventListener("change", () => {
      const groupInSelect = Array.from(select.options).find(
        option => option.value === checkbox.value
      );
      if (groupInSelect && !checkbox.checked) {
        if (usingOptionsChips) {
          clearSelectedOption(select, groupInSelect);
        } else {
          window.bbl.choices_js[select.id].removeActiveItemsByValue(
            groupInSelect.value
          );
        }
      } else if (!groupInSelect && checkbox.checked) {
        if (checkbox.labels.length) {
          addNewSelectedOption(
            checkbox.labels[0].textContent,
            checkbox.value,
            select.id
          );
          if (usingOptionsChips && inputTypesForOptionsChips) {
            resetSelectedTagsLinkedWithOptionsChips(
              form,
              inputTypesForOptionsChips,
              checkboxes
            );
          }
        }
      }
    });
  });
}

export function linkSelectOptionsWithCheckboxes(form, select, checkboxes) {
  if (select) {
    select.addEventListener("change", () => {
      checkboxes.forEach(checkbox => {
        checkbox.checked = Array.from(select.options).some(
          option => option.value === checkbox.value
        );
      });
    });
  }
}
