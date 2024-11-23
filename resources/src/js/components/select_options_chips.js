/**
 * Find the first radio button that has no value from a group of radio buttons.
 *
 * @param {HTMLElement} radio A radio button that is part of the group.
 *
 * @returns {HTMLElement|null} The radio element if found.
 */
function getEmptyRadio(radio) {
  return radio.form.querySelector("[name='" + radio.name + "'][value='']");
}

/**
 * Clear the value of a selected option.
 *
 * @param {HTMLElement} input The radio/checkbox to un-check or a select to deselect the
 * `option` from.
 * @param {HTMLElement} option The option to deselect when `input` is a select.
 */
function clearSelectedOption(input, option) {
  // Clear selected options that use Choices.js.
  if (window.bbl.choices_js[input.id]) {
    window.bbl.choices_js[input.id].removeActiveItemsByValue(option.value);
  } else {
    // Clear checkboxes and radios.
    input.checked = false;

    // If there is a Radio with no value, mark it as checked.
    // This is equivalent to no value.
    if (input.type === "radio") {
      const emptyRadio = getEmptyRadio(input);
      if (emptyRadio) {
        emptyRadio.checked = true;
      }
    }
  }
  input.dispatchEvent(new Event("change"));
}

/**
 * Create an HTML tag element with the given text.
 *
 * @param {String} text String that the tag should contain.
 * @param {HTMLInputElement} input
 * @param {HTMLOptionElement} option
 *
 * @returns {HTMLElement}
 */
function getTag(text, input, option = null) {
  const tag = document
    .querySelector("#ag-js-filterChipTemplate")
    .content.cloneNode(true);
  tag.querySelector(".ag-filter-chip__text").innerText = text;

  // Radios with no empty option can not be removed.
  if (input.type === "radio" && !getEmptyRadio(input)) {
    tag.querySelector(".ag-js-filterTag .i-close").remove();
    return tag;
  }

  tag.querySelector(".ag-js-filterTag").addEventListener("click", () => {
    clearSelectedOption(input, option);
    if (submitOnClearTag()) {
      input.form.submit();
    }
  });
  tag.querySelector(".ag-js-filterTag").addEventListener("dblclick", () => {
    clearSelectedOption(input, option);
  });
  return tag;
}

/**
 * Create and return selected options tags for the given form element.
 *
 * @param {HTMLElement} element The form element from which to create tags.
 *
 * @returns {HTMLElement[]} Array of tags.
 */
function getSelectedOptionsTags(element) {
  if (element.disabled) {
    return [];
  }
  if (element.type === "select-multiple") {
    return Array.from(element.selectedOptions).map(option => {
      return getTag(option.label, element, option);
    });
  }
  if (element.checked && element.value.length && element.labels.length) {
    return [getTag(element.labels[0].innerText, element)];
  }
  return [];
}

/**
 * Create and return all the selected options of the form.
 * @param {HTMLFormElement} form
 * @param {String[]} inputTypes
 * @returns {HTMLElement[]} Array of selected options.
 */
function getSelectedOptions(
  form,
  inputTypes = ["checkbox", "radio", "select", "select-multiple"]
) {
  return Array.from(form.elements).filter(element => {
    return inputTypes.includes(element.type);
  });
}

/**
 * Reset all the selected option tags for the form.
 * @param {String[]} inputTypes
 * @param {HTMLFormElement} form
 */
function resetSelectedOptionsTags(form, inputTypes) {
  const tags = getSelectedOptions(form, inputTypes).reduce(
    (accumulator, element) => {
      return accumulator.concat(getSelectedOptionsTags(element));
    },
    []
  );

  const hasSelectedOptions = tags.some(tag => {
    return tag.querySelector(".i-close");
  });
  document.querySelectorAll(".ag-js-filterDelete").forEach(button => {
    button.classList.toggle("ag-is-remove", !hasSelectedOptions);
  });

  document.querySelectorAll(".ag-js-filterSet").forEach(container => {
    container.innerHTML = "";
    container.append(...tags);
  });
}

function submitOnClearTag() {
  const submitOnClearTagValue = document.getElementById("submit_on_clear_tag");
  return submitOnClearTagValue && submitOnClearTagValue.value === "1";
}

function clearFormSelectedOptions(form) {
  document
    .querySelectorAll(".ag-js-filterChip .ag-js-filterTag")
    .forEach(tag => {
      tag.dispatchEvent(new Event("dblclick"));
    });
  if (submitOnClearTag()) {
    form.submit();
  }
}

export {
  clearFormSelectedOptions,
  getSelectedOptions,
  resetSelectedOptionsTags,
  clearSelectedOption
};
