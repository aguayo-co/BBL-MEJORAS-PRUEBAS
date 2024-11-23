const booleanOperatorFormClass = "ag-js-set";
const formsetSeparatorFormClass = "ag-js-separator_set";
const templateFormId = "boolean_form_template";
const addFormBtnClass = "ag-js-addSet";
const addFormBtnTemplateId = "formset_btn_add_template";
const templateFormGroupSeparatorId = "boolean_form_group_separator_template";
const addGroupBtnClass = "ag-js-addGroup";
const deleteFormBtnClass = "ag-js-btn_delete_boolean_operator";
const deleteFormBtnContainerClass =
  "ag-js-btn_delete_boolean_operator_container";
const modalDeleteBtn = {
  class: "ag-js-modal-delete__btn",
  dataFormId: "data-form-id"
};

function getPrefix() {
  return document.querySelector(".ag-js-formset_prefix").value;
}

function getFormsetContainers() {
  return document.getElementsByClassName("ag-js-formset");
}

function addBooleanOperator(btn, container) {
  const newForm = getNewForm();
  container.insertBefore(newForm, btn);
  updateFormsetIndexes(container);
  updateTotalFormsValue(container);
  preventLastBooleanOperatorDeletion(container);
}

function getNewForm() {
  return document.getElementById(templateFormId).content.cloneNode(true);
}

function addBooleanOperatorGroup(container) {
  const newFormGroupSeparator = document
    .getElementById(templateFormGroupSeparatorId)
    .content.cloneNode(true);

  const or_checkbox = newFormGroupSeparator.getElementById(
    `id_${newFormGroupSeparator.children[0].dataset.prefixId}-is_or`
  );
  or_checkbox.setAttribute("checked", "");

  const newFormGroupAddBtn = document
    .getElementById(addFormBtnTemplateId)
    .content.cloneNode(true);

  const newForm = document
    .getElementById(templateFormId)
    .content.cloneNode(true);

  container.appendChild(newFormGroupSeparator);

  container.appendChild(newForm);

  container.appendChild(newFormGroupAddBtn);

  updateFormsetIndexes(container);
  updateTotalFormsValue(container);
  preventLastBooleanOperatorDeletion(container);
}

function updateFormsetIndexes(container) {
  let i = 0;
  container.children.forEach(child => {
    if (
      child.classList.contains(booleanOperatorFormClass) ||
      child.classList.contains(formsetSeparatorFormClass)
    ) {
      updateFormIndex(i, child);
      i++;
    }
  });
}

function updateFormIndex(index, form) {
  const prefix = getPrefix();
  const id_regex = new RegExp(
    "(" + prefix + "-(\\d+|__prefix__|empty-form))",
    "g"
  );
  const replacement = prefix + "-" + index;
  form.setAttribute("id", replacement);
  form.removeAttribute("data-id-prefix");
  form.innerHTML = form.innerHTML.replace(id_regex, replacement);
}

function updateTotalFormsValue(container) {
  const prefix = getPrefix();
  const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
  let i = 0;
  container.children.forEach(child => {
    if (
      child.classList.contains(booleanOperatorFormClass) ||
      child.classList.contains(formsetSeparatorFormClass)
    ) {
      updateFormIndex(i, child);
      i++;
    }
  });
  totalForms.value = i;
}

function deleteBooleanOperator(id, container) {
  const form = document.getElementById(id);
  removeBooleanGroupIfNecessary(form);
  form.remove();
  updateTotalFormsValue(container);
  updateFormsetIndexes(container);
  preventLastBooleanOperatorDeletion(container);
}

function preventLastBooleanOperatorDeletion(container) {
  const totalForms = parseInt(
    document.getElementById(`id_${getPrefix()}-TOTAL_FORMS`).value
  );

  if (totalForms === 1) {
    const forms = container.getElementsByClassName(booleanOperatorFormClass);
    forms.forEach(form => {
      const buttons = form.getElementsByClassName(deleteFormBtnContainerClass);
      buttons.forEach(btn => {
        btn.remove();
      });
    });
  } else if (totalForms > 1) {
    const forms = container.getElementsByClassName(booleanOperatorFormClass);
    forms.forEach(form => {
      const buttons = form.getElementsByClassName(deleteFormBtnContainerClass);
      if (buttons.length === 0) {
        const newForm = getNewForm();
        newForm.children.forEach(child => {
          const newButtons = child.getElementsByClassName(
            deleteFormBtnContainerClass
          );
          newButtons.forEach(btn => {
            form.appendChild(btn);
            updateFormsetIndexes(container);
          });
        });
      }
    });
  }
}

function removeBooleanGroupIfNecessary(targetElement) {
  let previousSibling = targetElement.previousElementSibling;
  let nextSibling = targetElement.nextElementSibling;
  if (
    previousSibling &&
    nextSibling &&
    previousSibling.classList.contains(formsetSeparatorFormClass) &&
    nextSibling.classList.contains(addFormBtnClass)
  ) {
    previousSibling.remove();
    nextSibling.remove();
  }

  let secondNextSibling = nextSibling.nextElementSibling;
  if (
    previousSibling === null &&
    nextSibling &&
    nextSibling.classList.contains(addFormBtnClass) &&
    secondNextSibling.classList.contains(formsetSeparatorFormClass)
  ) {
    nextSibling.remove();
    secondNextSibling.remove();
  }
}

function initFormsetHandler() {
  getFormsetContainers().forEach(container => {
    //
    updateTotalFormsValue(container);
    preventLastBooleanOperatorDeletion(container);

    // Formset click event delegation
    container.addEventListener("click", function(e) {
      const element = e.target;
      // Set data-form-id on modal delete button
      if (
        element &&
        element.classList.contains(deleteFormBtnClass) &&
        element.dataset.parentFormId
      ) {
        const modalDeleteButtons = document.getElementsByClassName(
          modalDeleteBtn.class
        );

        modalDeleteButtons.forEach(btn => {
          btn.setAttribute(
            modalDeleteBtn.dataFormId,
            element.dataset.parentFormId
          );
        });
      }

      // Add new boolean form
      if (element && element.classList.contains(addFormBtnClass)) {
        addBooleanOperator(element, this);
      }
    });

    // Keep formset's input changes marked in html
    container.addEventListener("change", function(e) {
      let element = e.target;
      if (element && element.tagName === "SELECT") {
        element.options.forEach(option => {
          if (element.value === option.value) {
            option.setAttribute("selected", "");
          } else {
            option.removeAttribute("selected");
          }
        });
      }
      if (element && element.tagName === "INPUT" && element.type === "text") {
        element.setAttribute("value", element.value);
      }
    });

    // Add group event listener
    const addGroupButtons = document.getElementsByClassName(addGroupBtnClass);
    addGroupButtons.forEach(btn => {
      btn.addEventListener("click", function() {
        addBooleanOperatorGroup(container);
      });
    });

    // Delete boolean form event listener
    const modalDeleteButtons = document.getElementsByClassName(
      modalDeleteBtn.class
    );
    modalDeleteButtons.forEach(btn => {
      btn.addEventListener("click", function() {
        deleteBooleanOperator(this.dataset.formId, container);
      });
    });
  });
}

function initCleanSearchBtnHandler() {
  // Eliminar reset btn y limpiar input durante el evento "reset" del form
  var cleanBtn = document.querySelectorAll(".ag-js-cleanAdvancedSearchForm");
  cleanBtn.forEach(btn => {
    btn.addEventListener("click", () => {
      getFormsetContainers().forEach(container => {
        const form = container.closest("#search_form");
        Array.from(container.children).forEach(child => {
          child.remove();
        });
        const newFormGroupAddBtn = document
          .getElementById(addFormBtnTemplateId)
          .content.cloneNode(true);

        const newForm = document
          .getElementById(templateFormId)
          .content.cloneNode(true);

        container.appendChild(newForm);

        container.appendChild(newFormGroupAddBtn);

        updateFormsetIndexes(container);
        updateTotalFormsValue(container);
        preventLastBooleanOperatorDeletion(container);

        form.scrollIntoView(true);
      });

      const searchTextInput = document.getElementById("id_search_text");
      searchTextInput.removeAttribute("value");
      searchTextInput.value = null;
      searchTextInput.dispatchEvent(new Event("input"));

      const publishYears = [
        document.getElementById("id_from_publish_year"),
        document.getElementById("id_to_publish_year")
      ];
      publishYears.forEach(dateInput => {
        dateInput.value = null;
        searchTextInput.removeAttribute("value");
      });
    });
  });
}

initFormsetHandler();
initCleanSearchBtnHandler();
