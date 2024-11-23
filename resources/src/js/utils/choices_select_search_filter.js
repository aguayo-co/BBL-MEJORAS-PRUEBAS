import Choices from "choices.js";

window.bbl = window.bbl || {};
window.bbl.choices_js = window.bbl.choices_js || {};

const defaultChoicesUserConfig = {
  itemSelectText: "",
  removeItems: true,
  removeItemButton: true,
  classNames: {
    containerOuter: "ag-select-search",
    containerInner: "ag-select-search__inner",
    input: "ag-select-search__input",
    inputCloned: "ag-select-search__input-cloned",
    list: "ag-select-search__list",
    listItems: "ag-select-search__list-multiple",
    listDropdown: "ag-select-search__list-dropdown",
    item: "ag-select-search__item",
    itemSelectable: "ag-select-search__item-selectable",
    itemDisabled: "ag-select-search__item-disabled",
    itemChoice: "ag-select-search__item-choice",
    placeholder: "ag-select-search__placeholder",
    button: "ag-select-search__button",
    activeState: "ag-is-show",
    focusState: "ag-is-focused",
    openState: "ag-is-show",
    highlightedState: "ag-is-highlighted",
    hiddenState: "ag-is-hidden"
  }
};

function initChoicesJs(choicesWrapper, choicesUserConfig) {
  choicesWrapper.querySelectorAll("select").forEach(select => {
    window.bbl.choices_js[select.id] = new Choices(select, choicesUserConfig);
  });
  const placeholder = choicesWrapper.dataset.placeholder;
  const searchInput = choicesWrapper.querySelectorAll(
    ".ag-select-search__input"
  );
  searchInput.forEach(input => {
    input.setAttribute("placeholder", placeholder);
    if (input.options && input.options.length > 0) {
      choicesWrapper.classList.add("ag-is-choiceSelected");
    }
    if (input.type === "text") {
      input.setAttribute("id", "input-selectsearch");
      input.setAttribute("aria-labelledby", "input-selectsearch");
    }
  });
}

function addNewSelectedOption(optionLabel, optionValue, selectElementId) {
  if (!optionValue) {
    optionValue = `new_option__name=${optionLabel}`;
  }
  window.bbl.choices_js[selectElementId].setChoices(
    [
      {
        value: optionValue,
        label: optionLabel,
        selected: true
      }
    ],
    "value",
    "label",
    false
  );
}

(function() {
  setTimeout(() => {
    const searchInput = document.querySelectorAll(".ag-select-search__inner");
    searchInput.forEach(input => {
      input.addEventListener("click", () => {
        setTimeout(() => {
          if (input.closest(".ag-is-show")) {
            document.querySelector(
              ".ag-c-filter__button_sticky"
            ).style.marginTop = "250px";
          }
        }, 50);
      });
    });
  }, 500);
})();

export { defaultChoicesUserConfig, initChoicesJs, addNewSelectedOption };
