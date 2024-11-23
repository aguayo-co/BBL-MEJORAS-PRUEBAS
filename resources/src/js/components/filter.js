function activeFilterItem(item) {
  if (item) {
    item.style.display = "block";
    item.removeAttribute("disabled");
  }
}

function disableFilterItem(item) {
  if (item) {
    item.style.display = "none";
    item.setAttribute("disabled", "disabled");
  }
}

// Funcionalidad filtro Content Model
const filterContentModel = function() {
  const contentModelInput = document.querySelector(
    "input[name='content_model']:checked"
  );
  if (contentModelInput) {
    const filterItems = Array.from(
      document.getElementsByClassName("ag-js-filterItem")
    );
    const filterItemsTitle = document.querySelector(".ag-js-filter-side-title");
    filterItems.forEach(item => {
      disableFilterItem(item);
    });
    switch (contentModelInput.value) {
      case "harvester.contentresource":
        filterItemsTitle.classList.remove("ag-is-hide");
        filterItems
          .filter(item => !["collection_type"].includes(item.dataset.name))
          .forEach(item => {
            item.style.display = "block";
            item.removeAttribute("disabled");
          });
        break;
      case "harvester.collection":
        filterItemsTitle.classList.remove("ag-is-hide");
        ["content_model", "collection_type", "data_sources"].forEach(name => {
          const item = document.querySelector(
            '.ag-js-filterItem[data-name="' + name + '"]'
          );
          if (item) {
            activeFilterItem(item);
          }
        });
        break;
      case "expositions.exposition":
        filterItemsTitle.classList.add("ag-is-hide");
        filterItems.forEach(item => {
          disableFilterItem(item);
        });
        break;
    }
  }
};

(function() {
  const aside = document.getElementsByClassName("ag-js-aside")[0];
  // Open aside form on click button "Filtrar"
  const btnOpenFilterMobile = document.getElementsByClassName(
    "ag-js-asideOpen"
  )[0];

  if (btnOpenFilterMobile) {
    btnOpenFilterMobile.addEventListener("click", function() {
      aside.classList.add("ag-is-aside_open");
      if (aside.closest(".ag-is-element-closest-filter")) {
        aside
          .closest(".ag-is-element-closest-filter")
          .classList.add("ag-is-aside_parent");
      }
    });
  }

  const btnCloseFilterMobile = document.getElementsByClassName(
    "ag-js-asideClose"
  )[0];
  if (btnCloseFilterMobile) {
    // Close aside form on click button "X"
    btnCloseFilterMobile.addEventListener("click", function() {
      aside.classList.remove("ag-is-aside_open");
      if (aside.closest(".ag-is-element-closest-filter")) {
        aside
          .closest(".ag-is-element-closest-filter")
          .classList.remove("ag-is-aside_parent");
      }
    });
    // Close aside form on click out of form container
    document.addEventListener("mouseup", function(e) {
      const asideContent = document.getElementsByClassName(
        "ag-js-asideContent"
      )[0];
      if (
        !asideContent.contains(e.target) &&
        aside.classList.contains("ag-is-aside_open")
      ) {
        aside.classList.remove("ag-is-aside_open");
        if (aside.closest(".ag-is-element-closest-filter")) {
          aside
            .closest(".ag-is-element-closest-filter")
            .classList.remove("ag-is-aside_parent");
        }
        document.documentElement.scrollTo({
          top: 0,
          left: 0,
          behavior: "smooth"
        });
      }
    });
  }

  filterContentModel();

  // The form is submit if the value is changed in any input of the filter form.
  if (aside) {
    const filterInputs = document.getElementsByClassName(
      "ag-js-searchFilter"
    )[0]
      ? Array.from(
          document
            .getElementsByClassName("ag-js-searchFilter")[0]
            .querySelectorAll("input, select")
        )
      : undefined;
    if (filterInputs) {
      filterInputs.forEach(x => {
        x.addEventListener("change", function() {
          filterContentModel();
          this.form.submit();
        });
      });
    }
  }

  // Filtro tema(subject)
  const subjectInput = document.getElementsByName("subject")[0];
  if (subjectInput) {
    if (subjectInput.options.length > 0) {
      document
        .getElementsByClassName("ag-js-choices")[0]
        .classList.add("ag-is-choiceSelected");
    }
  }

  // Botón mobile filtro, scroll top
  const filterBtn = Array.from(
    document.getElementsByClassName("ag-js-filterBtn")
  );
  if (filterBtn[0]) {
    filterBtn.forEach(btn => {
      btn.addEventListener("click", function() {
        window.scrollTo(0, 0);
      });
    });
  }

  // boton filtrar funcionalidad
  const btnFilterSubmit = document.getElementsByClassName(
    "ag-js-filterSubmit"
  )[0];
  btnFilterSubmit &&
    btnFilterSubmit.addEventListener("click", function() {
      document
        .querySelector(".ag-js-searchTextInputContainer")
        .classList.add("ag-is-default");
      this.form.submit();
    });
})();

export { activeFilterItem, disableFilterItem, filterContentModel };
