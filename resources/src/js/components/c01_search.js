import axios from "axios";
import {
  activeFilterItem,
  disableFilterItem,
  filterContentModel
} from "./filter";

const searchTextInputContainerClass = "ag-js-searchTextInputContainer";

// GETTERS

/**
 * Busca el form a partir de un id
 *
 * @returns {HTMLElement|undefined} El elemento form si lo encuentra
 */
function getSearchForm() {
  return document.getElementById("search_form");
}

/**
 * Busca los search text input a partir de un atributo name
 *
 * @returns {NodeList}
 */
function getSearchTextInputs(form) {
  return form.querySelectorAll(
    `.${searchTextInputContainerClass} [name="search_text"]`
  );
}

/**
 * Busca los container de sugerencias a partir de una clase
 *
 * @returns {HTMLCollection}
 */
function getSuggestionsBoxes(form) {
  return form.getElementsByClassName("ag-js-searchSuggestion");
}

/**
 * Busca los container de tipos de contenido a partir de una clase
 *
 * @returns {HTMLCollection}
 */
function getContentTypeCheckboxContainers(form) {
  return form.getElementsByClassName("ag-js-contentTypeCheckboxContainer");
}

/**
 * Busca los container de tooltip
 * dentro de un container de search text input a partir de una clase
 *
 * @returns {Array} Array de elementos HTML
 *
 */
function getTooltipsSearch(searchTextInputContainer) {
  return searchTextInputContainer.querySelectorAll(`.ag-js-tip`);
}

function getSearchBtnMobile() {
  return document.getElementsByClassName("ag-js-searchBtnMobile");
}

function getContentTypeRadioButtons(form) {
  return form.querySelectorAll('input[type="radio"][name="content_model"]');
}

function getCollectionTypeCheckboxes(form) {
  return Array.from(
    form.querySelectorAll('input[type="checkbox"][name="collection_type"]')
  );
}

function getDataSourcesFieldset(form) {
  return form.querySelector('.ag-js-filterItem[data-name="data_sources"]');
}

// HELPERS

function showTooltipsSearch(searchTextInputContainer) {
  const tooltipSearch = getTooltipsSearch(searchTextInputContainer);
  tooltipSearch.forEach(tip => {
    tip.removeAttribute("hidden");
    tip.classList.add("ag-is-show");
  });
}

function hideTooltipsSearch(searchTextInputContainer) {
  const tooltipSearch = getTooltipsSearch(searchTextInputContainer);
  tooltipSearch.forEach(tip => {
    tip.setAttribute("hidden", "hidden");
    tip.classList.remove("ag-is-show");
  });
}

// Generador del html final donde se muestran las sugerencias
function getSuggestionsTemplate(data, textSearch) {
  const title =
    data.contentresource.length ||
    data.collection.length ||
    data.exposition.length
      ? '<p class="ag-c-search__title">Sugerencias de búsqueda</p>'
      : "";

  // Expresión regular que se usa para colocar en negrilla el texto buscado, se utiliza .replace(regex, value => `<strong class="ag-c-search__term">${value}</strong>`) para colocar el texto en negrilla.
  const regex = new RegExp(textSearch, "gi");

  // Limitar a máximo 3 sugerencias por categoría
  [data.contentresource, data.collection, data.exposition].forEach(data => {
    data.length > 3 && (data.length = 3);
  });

  const contentresource = data.contentresource.length
    ? `
      <p class="ag-c-search__subtitle">Contenidos</p>
      <ul class="ag-c-search__suggestion">
        ${data.contentresource
          .map(
            suggestion =>
              `<li class="ag-c-search__item ag-js-searchSuggestionItem" data-content-type="harvester.contentresource"><a class="ag-c-search__link" href="#">${suggestion.title.replace(
                regex,
                value => `<strong class="ag-c-search__term">${value}</strong>`
              )}</a></li>`
          )
          .join("")}
      </ul>
    `
    : "";

  const collection = data.collection.length
    ? `
      <p class="ag-c-search__subtitle">Colecciones</p>
      <ul class="ag-c-search__suggestion">
        ${data.collection
          .map(
            suggestion =>
              `<li class="ag-c-search__item ag-js-searchSuggestionItem" data-content-type="harvester.collection"><a class="ag-c-search__link" href="#">${suggestion.title.replace(
                regex,
                value => `<strong class="ag-c-search__term">${value}</strong>`
              )}</a></li>`
          )
          .join("")}
      </ul>
    `
    : "";

  const exposition = data.exposition.length
    ? `
      <p class="ag-c-search__subtitle">Exposiciones</p>
      <ul class="ag-c-search__suggestion">
        ${data.exposition
          .map(
            suggestion =>
              `<li class="ag-c-search__item ag-js-searchSuggestionItem" data-content-type="expositions.exposition"><a class="ag-c-search__link" href="#">${suggestion.title.replace(
                regex,
                value => `<strong class="ag-c-search__term">${value}</strong>`
              )}</a></li>`
          )
          .join("")}
      </ul>
    `
    : "";

  return `
      ${title}
      ${contentresource}
      ${collection}
      ${exposition}
    `;
}

function setHeightToSuggestedSearchList(suggestionBox, method) {
  const suggestedSearchList = suggestionBox.closest(
    ".ag-js-suggestedSearchList"
  );
  const heightClassName = "ag-is-filter_height";
  if (suggestedSearchList && method === "add") {
    suggestedSearchList.classList.add(heightClassName);
  }
  if (suggestedSearchList && method === "remove") {
    suggestedSearchList.classList.remove(heightClassName);
  }
}

function showSuggestionsOnKeyup() {
  getSearchTextInputs(getSearchForm()).forEach(input => {
    input.addEventListener("keyup", function() {
      if (input.value.length >= 3) {
        axios
          .get("/search/suggestions?search_text=" + input.value)
          .then(function(response) {
            let data = response.data;
            if (
              data.collection.length ||
              data.contentresource.length ||
              data.exposition.length
            ) {
              getSuggestionsBoxes(input.form).forEach(box => {
                box.innerHTML = getSuggestionsTemplate(
                  response.data,
                  input.value
                );
                box.classList.remove("ag-is-hide");

                let searchSuggestionItems = box.getElementsByClassName(
                  "ag-js-searchSuggestionItem"
                );
                searchSuggestionItems.forEach(suggestion => {
                  suggestion.addEventListener("click", function() {
                    const contentTypeRadioButtons = getContentTypeRadioButtons(
                      input.form
                    );
                    contentTypeRadioButtons.forEach(checkbox => {
                      if (checkbox.value === this.dataset.contentType) {
                        checkbox.checked = true;
                      }
                    });
                    input.value = suggestion.innerText;
                    input.form.submit();
                  });
                });
                setHeightToSuggestedSearchList(box, "add");
              });
            }
          });
      } else {
        getSuggestionsBoxes(input.form).forEach(box => {
          box.innerHTML = "";
          box.classList.add("ag-is-hide");
          setHeightToSuggestedSearchList(box, "remove");
        });
      }
    });
  });
}

function hideSuggestionsOnMouseUp(form) {
  document.addEventListener("mouseup", function(e) {
    if (!form.contains(e.target)) {
      configForHideSuggestionBox(form);
    }
  });
}

function hideSuggestionsWhenBlurInput() {
  const form = document.getElementById("search_form");
  const btnForm = form.querySelector(".ag-c-filter__button_sticky");

  form.addEventListener(
    "blur",
    () => {
      console.log("hideSuggestionsWhenBlurInput()");
      configForHideSuggestionBox(form);
      if (btnForm.style) {
        btnForm.style = "";
      }
    },
    true
  );
}

function configForHideSuggestionBox(form) {
  getSuggestionsBoxes(form).forEach(box => {
    box.classList.add("ag-is-hide");
    setHeightToSuggestedSearchList(box, "remove");
  });
}

/**
 * Controlador de cambios en checkboxes de tipo de contenido
 *
 * @param {HTMLElement} container
 *
 */
function contentTypeCheckboxesChangeHandler(container) {
  const itemsChecked = container.querySelectorAll(
    '[name="content_type"]:checked'
  );
  const checkboxAll = container.getElementsByClassName("ag-js-checkAll");
  const contentTypeBtn = container.getElementsByClassName(
    "ag-js-contentTypeBtn"
  );
  if (itemsChecked.length) {
    checkboxAll.forEach(checkbox => {
      checkbox.checked = false;
    });
    contentTypeBtn.forEach(btn => {
      btn.innerText =
        itemsChecked.length > 1
          ? "Varios"
          : container.querySelector(`[for='${itemsChecked[0].id}']`).innerText;
    });
  } else {
    checkboxAll.forEach(checkbox => {
      checkbox.checked = true;
    });
    contentTypeBtn.forEach(btn => {
      btn.innerText = "Tipo de contenido";
    });
  }
}

/**
 * Marca la opción "todos" en checkboxes de tipo de contenido
 *
 * @param {HTMLElement} container
 *
 */
function checkCheckboxAll(container) {
  const contentTypeCheckBoxes = container.querySelectorAll(
    '[name="content_type"]'
  );
  const checkboxAll = container.getElementsByClassName("ag-js-checkAll");
  const contentTypeBtn = container.getElementsByClassName(
    "ag-js-contentTypeBtn"
  );
  contentTypeCheckBoxes.forEach(checkbox => {
    checkbox.checked = false;
  });
  checkboxAll.forEach(checkbox => {
    checkbox.checked = true;
  });
  contentTypeBtn.forEach(btn => {
    btn.innerText = "Tipo de contenido";
  });
}

/**
 * Cierra el dropdown de tipo de contenido al hacer click afuera del elemento
 *
 * @param {HTMLElement} container
 *
 */
function closeDropDownList(container) {
  const dropDownUl = container.getElementsByClassName("ag-js-dropdownSlide");
  const dropdownBtn = container.getElementsByClassName("ag-js-dropdownBtn");

  dropDownUl.forEach(ul => {
    ul.classList.remove("ag-is-dropdownOpen");
  });
  dropdownBtn.forEach(btn => {
    btn.classList.remove("ag-is-searchOpen");
    btn.classList.remove("i-after-arrow-up");
    btn.classList.add("i-after-arrow-down");
  });
}

function getContentTypeItemsChecked(form) {
  let itemsChecked = 0;
  getContentTypeCheckboxContainers(form).forEach(container => {
    itemsChecked += container.querySelectorAll('[name="content_type"]:checked')
      .length;
  });
  return itemsChecked;
}

// CONTROLADORES

// Controlador de funcionalidad "Quizá quisiste decir"
function initDidYouMeanTextHandler() {
  /**
   * Funcionalidad sugerencia "Quizás quisiste decir", al darle click
   * en la corrección se coloca el texto en el input de 'search' y se hace submit.
   */
  const didyoumeanTextBtn = document.getElementsByClassName(
    "ag-js-didyoumeanText"
  );
  didyoumeanTextBtn.forEach(btn => {
    btn.addEventListener("click", function() {
      getSearchTextInputs(getSearchForm()).forEach(input => {
        input.value = this.innerText;
        input.form.submit();
      });
    });
  });
}

// Controlador de lista de sugerencias de búsqueda
function initSuggestionsBoxHandler() {
  /**
   * Agregamos al input de búsqueda el evento keyup, para que vaya
   * buscando las sugerencias a medida que se teclea en el input.
   */
  showSuggestionsOnKeyup();

  /**
   * Ocultar lista de sugerencias de búsqueda al desenfocar
   * la entrada de resultados de busqueda
   */
  hideSuggestionsWhenBlurInput();

  // Ocultar lista de sugerencias de búsqueda al dar clic fuera del contenedor
  // hideSuggestionsOnMouseUp(getSearchForm());
}

// Controlador del contenedor de checkboxes tipo de contenido
function initContentTypeCheckboxHandler() {
  getContentTypeCheckboxContainers(getSearchForm()).forEach(container => {
    // Marcar checkbox "todos" por defecto
    checkCheckboxAll(container);

    // Desmarcar todas los demás checkboxes al marcar "todos"
    const checkboxAll = container.getElementsByClassName("ag-js-checkAll");
    checkboxAll.forEach(checkbox => {
      checkbox.addEventListener("change", function() {
        checkCheckboxAll(container);
      });
    });

    // Controlador de cambios en los checkboxes tipo de contenido
    const contentTypeCheckBoxes = container.querySelectorAll(
      '[name="content_type"]'
    );
    contentTypeCheckBoxes.forEach(checkbox => {
      checkbox.addEventListener("change", function() {
        contentTypeCheckboxesChangeHandler(container);
      });
    });

    // Cerrar el dropdown de tipo de contenido al hacer click afuera del elemento
    document.addEventListener("mouseup", function(e) {
      if (!container.contains(e.target)) {
        closeDropDownList(container);
      }
    });
  });
}

function initSearchTextEventsHandler() {
  getSearchTextInputs(getSearchForm()).forEach(input => {
    input.addEventListener("input", function() {
      if (this.value.length >= 3) {
        const searchTextInputContainer = this.closest(
          `.${searchTextInputContainerClass}`
        );
        hideTooltipsSearch(searchTextInputContainer);
        searchTextInputContainer.classList.remove("ag-is-warning");
      }
    });

    input.addEventListener("invalid", function(e) {
      e.preventDefault();
      const searchTextInputContainer = this.closest(
        `.${searchTextInputContainerClass}`
      );

      if (getContentTypeItemsChecked(this.form)) {
        hideTooltipsSearch(searchTextInputContainer);
        searchTextInputContainer.classList.remove("ag-is-warning");
        this.form.submit();
        return;
      }
      showTooltipsSearch(searchTextInputContainer);
      searchTextInputContainer.classList.add("ag-is-warning");
      document.documentElement.scrollTo({
        top: 0,
        left: 0,
        behavior: "smooth"
      });
    });

    input.form.addEventListener(
      "submit",
      function(e) {
        const input = input;
        e.preventDefault();
        const searchTextInputContainer = this.closest(
          `.${searchTextInputContainerClass}`
        );

        if (
          getContentTypeItemsChecked(this.form) === 0 &&
          this.value.length < 3
        ) {
          showTooltipsSearch(searchTextInputContainer);
          searchTextInputContainer.classList.add("ag-is-warning");
          document.documentElement.scrollTo({
            top: 0,
            left: 0,
            behavior: "smooth"
          });
        } else {
          hideTooltipsSearch(searchTextInputContainer);
          searchTextInputContainer.classList.remove("ag-is-warning");
          this.form.submit();
        }
      }.bind(input)
    );

    document.addEventListener("mouseup", function(e) {
      if (!input.form.contains(e.target)) {
        const searchTextInputContainer = input.closest(
          `.${searchTextInputContainerClass}`
        );
        hideTooltipsSearch(searchTextInputContainer);
        searchTextInputContainer.classList.remove("ag-is-warning");
      }
    });
  });
}

function initSearchBtnMobileHandler() {
  const searchBtnMobile = getSearchBtnMobile();

  searchBtnMobile.forEach(btn => {
    btn.addEventListener("click", function() {
      const btnMenu = document.getElementsByClassName("ag-js-btnOpenMenu");
      const contentMenu = document.getElementsByClassName("ag-js-subMenu");

      btnMenu.forEach(_btn => {
        _btn.classList.remove("ag-is-active");
      });

      contentMenu.forEach(content => {
        content.classList.remove("ag-is-menu_showmobile");
        content.classList.add("ag-is-menu_hidemobile");
      });
    });
  });
}

function initInputSearchResetBtnHandler() {
  getSearchTextInputs(getSearchForm()).forEach(input => {
    if (!input.closest(".ag-js-inputReset")) {
      return;
    }

    input.addEventListener("input", function() {
      this.closest(".ag-js-inputReset").classList.toggle(
        "ag-is-reset-off",
        !this.value.length
      );
    });
    input.dispatchEvent(new Event("input"));

    const resetButton = input
      .closest(".ag-js-inputReset")
      .querySelector(".ag-js-inputResetBtn");
    // Eliminar reset btn y limpiar input durante el evento "click" del reset btn
    resetButton.addEventListener("click", function() {
      const input = this.parentNode.querySelector("input");
      input.value = "";
      input.dispatchEvent(new Event("input"));
    });
  });
}

function initResetFormHandler() {
  // Eliminar reset btn y limpiar input durante el evento "reset" del form
  getSearchForm().addEventListener("reset", function() {
    getSearchTextInputs().forEach(input => {
      input.setAttribute("value", "");
      input.dispatchEvent(new Event("input"));
    });
  });
}

function initCleanAdvancedSearchBtn() {
  const buttons = document.querySelectorAll(
    ".ag-js-cleanAdvancedSearchFromBasic"
  );
  var exactSearch = document.querySelector("#id_exact_search");
  var asideFormsAdvancedSearch = document.querySelectorAll(
    ".ag-js-asideFormAdvancedSearch"
  );
  buttons.forEach(btn => {
    btn.addEventListener("click", function() {
      if (asideFormsAdvancedSearch) {
        asideFormsAdvancedSearch.forEach(asideFormAdvancedSearch => {
          asideFormAdvancedSearch.remove();
        });
      }

      if (exactSearch) {
        exactSearch.removeAttribute("checked");
      }

      getSearchForm().submit();
    });
  });
}

function initScrollEvents() {
  window.addEventListener("scroll", () => {
    toggleClassFilterFixed();
  });
}

function initFilterFixedOnPageLoad() {
  toggleClassFilterFixed();
}

function toggleClassFilterFixed() {
  const searchFixBarWrapper = document.querySelector(".ag-js-wrapFixBar");
  if (searchFixBarWrapper) {
    if (window.pageYOffset === 0) {
      searchFixBarWrapper.classList.remove("ag-is-filter-fixed_top");
    } else {
      searchFixBarWrapper.classList.add("ag-is-filter-fixed_top");
    }
  }
}

function syncApplyFiltersButtonWithSubmitFormButton() {
  const applyFiltersButton = document.querySelector(
    ".ag-js-apply_filters_extra_button"
  );
  if (applyFiltersButton) {
    applyFiltersButton.addEventListener("click", () =>
      getSearchForm().submit()
    );
  }
}

function initContentTypeInputEventsHandler() {
  const contentTypeRadioButtons = getContentTypeRadioButtons(getSearchForm());
  contentTypeRadioButtons.forEach(radioBtn => {
    radioBtn.addEventListener("change", () => filterContentModel());
  });
}

function toggleDataSourcesFieldset() {
  const collectionTypeCheckboxes = getCollectionTypeCheckboxes(getSearchForm());
  const collectionTypeCheckboxesChecked = collectionTypeCheckboxes.filter(
    checkbox => checkbox.checked
  );
  const collectionTypeSetChecked = collectionTypeCheckboxesChecked.some(
    checkbox => checkbox.value === "set"
  );
  const dataSourcesFieldset = getDataSourcesFieldset(getSearchForm());
  if (collectionTypeCheckboxesChecked.length && !collectionTypeSetChecked) {
    disableFilterItem(dataSourcesFieldset);
    const selectElement = dataSourcesFieldset.querySelector("#id_data_sources");
    Array.from(selectElement.options).forEach(option =>
      option.removeAttribute("selected")
    );
    selectElement.dispatchEvent(new Event("change"));
  } else {
    activeFilterItem(dataSourcesFieldset);
  }
}

function initCollectionTypeEventsHandler() {
  const collectionTypeCheckboxes = getCollectionTypeCheckboxes(getSearchForm());
  collectionTypeCheckboxes.forEach(checkbox => {
    checkbox.addEventListener("change", () => toggleDataSourcesFieldset());
  });
  toggleDataSourcesFieldset();
}

window.addEventListener("load", () => {
  if (getSearchForm()) {
    initFilterFixedOnPageLoad();
    initDidYouMeanTextHandler();
    initSuggestionsBoxHandler();
    initContentTypeCheckboxHandler();
    initSearchTextEventsHandler();
    initSearchBtnMobileHandler();
    initInputSearchResetBtnHandler();
    initResetFormHandler();
    initCleanAdvancedSearchBtn();
    initScrollEvents();
    syncApplyFiltersButtonWithSubmitFormButton();
    initContentTypeInputEventsHandler();
    initCollectionTypeEventsHandler();
  }
});
