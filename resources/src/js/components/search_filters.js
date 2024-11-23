import {
  clearFormSelectedOptions,
  getSelectedOptions,
  resetSelectedOptionsTags
} from "./select_options_chips";

if ("search_form" in document.forms) {
  const form = document.forms["search_form"];

  // Clear all filters action.
  document.querySelectorAll(".ag-js-filterDelete").forEach(element => {
    element.addEventListener("click", () => clearFormSelectedOptions(form));
  });

  // Reset tags filter on "reset" form event
  form.addEventListener("reset", () => clearFormSelectedOptions(form));

  // Reset tags on filter change.
  getSelectedOptions(form).forEach(element => {
    element.addEventListener("change", () => {
      resetSelectedOptionsTags(form);
      const alertMessageFiltersChanged = document.querySelector(
        ".ag-js-alert_message_filters_changed"
      );
      if (alertMessageFiltersChanged) {
        alertMessageFiltersChanged.classList.remove("ag-is-display-none");
      }
    });
  });
  resetSelectedOptionsTags(form);
}
