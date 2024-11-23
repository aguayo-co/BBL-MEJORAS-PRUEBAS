function resetDropdownForDesktop() {
  // Sólo si el Dropdown se necesita abierto en móvil y cerrado en desktop
  // Se debe colocar las clase "ag-js-dropdownOpenInMobile" al contenedor del dropdown
  const containerParent = Array.from(
    document.getElementsByClassName("ag-js-dropdownOpenInMobile")
  );

  containerParent.forEach(currentContainer => {
    const getCurrentContainer = currentContainer.querySelector(
      ".ag-js-dropdownBtn"
    );
    const getParentContainer = currentContainer.querySelector(
      ".ag-js-dropdownSlide"
    );

    if (
      currentContainer.classList.contains("ag-js-dropdownOpenInMobile") &&
      window.innerWidth >= 768
    ) {
      getCurrentContainer.classList.remove("ag-is-searchOpen");
      getCurrentContainer.classList.remove("i-after-arrow-up");
      getCurrentContainer.classList.add("i-after-arrow-down");

      getParentContainer.classList.remove("ag-is-dropdownOpen");
      getParentContainer.classList.add("ag-is-hidden");
    }

    if (
      currentContainer.classList.contains("ag-js-dropdownOpenInMobile") &&
      window.innerWidth <= 767
    ) {
      getCurrentContainer.classList.add("ag-is-searchOpen");
      getCurrentContainer.classList.remove("i-after-arrow-down");
      getCurrentContainer.classList.add("i-after-arrow-up");

      getParentContainer.classList.add("ag-is-dropdownOpen");
      getParentContainer.classList.remove("ag-is-hidden");
    }
  });
}

window.addEventListener("resize", () => {
  resetDropdownForDesktop();
});

(function dropdown() {
  const dropdownBtn = document.getElementsByClassName("ag-js-dropdownBtn");
  // aside menu for expositions
  const asideMenu = document.querySelector(".ag-js-asideMenuNav");

  resetDropdownForDesktop();

  for (let index = 0; index < dropdownBtn.length; index++) {
    dropdownBtn[index].addEventListener("click", function(ev) {
      if (this.hasAttribute("data-dropdown")) {
        // Funcionalidad b04_list
        const dropdownButtons = document.querySelectorAll(
          ".ag-js-dropdownBtn[data-dropdown]"
        );
        const dropdownContentAll = document.querySelectorAll(
          ".ag-js-dropdownSlide[data-dropdown]"
        );
        const dropdownBind = this.getAttribute("data-dropdown");
        const itemContainer = this.closest(".ag-js-itemList");
        const dropdownContent = itemContainer.querySelector(
          '.ag-js-dropdownSlide[data-dropdown="' + dropdownBind + '"]'
        );
        const elemIsClose = !dropdownContent.classList.contains(
          "ag-is-dropdownOpen"
        );

        // Al estar uno abierto la clase .ag-list__row adquiere la clase .ag-is-active.
        const itemsList = document.getElementsByClassName("ag-js-itemList");
        for (let i = 0; i < itemsList.length; i++) {
          itemsList[i]
            .getElementsByClassName("ag-list__row")[0]
            .classList.remove("ag-is-active");
        }
        itemContainer
          .getElementsByClassName("ag-list__row")[0]
          .classList.add("ag-is-active");

        // Oculta los demás dropdown
        for (let i = 0; i < dropdownContentAll.length; i++) {
          dropdownContentAll[i].classList.remove("ag-is-dropdownOpen");
          dropdownButtons[i].innerText.toLowerCase() == "ocultar detalles" &&
            (dropdownButtons[i].innerText = "Ver detalles");
          dropdownButtons[i].classList.remove("i-after-arrow-up");
          dropdownButtons[i].classList.add("i-after-arrow-down");
        }

        // Muestra u oculta el dropdown clickeado
        if (elemIsClose) {
          dropdownContent.classList.add("ag-is-dropdownOpen");
          this.classList.remove("i-after-arrow-down");
          this.classList.add("i-after-arrow-up");
          this.innerText.toLowerCase() == "ver detalles" &&
            (this.innerText = "Ocultar detalles");
        } else {
          itemContainer
            .getElementsByClassName("ag-list__row")[0]
            .classList.remove("ag-is-active");
          dropdownContent.classList.remove("ag-is-dropdownOpen");
          this.classList.remove("i-after-arrow-up");
          this.classList.add("i-after-arrow-down");
          this.innerText.toLowerCase() == "ocultar detalles" &&
            (this.innerText = "Ver detalles");
        }
      } else {
        // Funcionalidad c06_dropdown
        const btn = ev.target;
        const container = btn.parentElement;
        const content = container.getElementsByClassName(
          "ag-js-dropdownSlide"
        )[0];
        if (
          container.classList.contains("ag-js-dropdownMobile") &&
          window.innerWidth >= 768
        ) {
          content.classList.remove("ag-is-dropdownOpen");
          return;
        }
        if (content) {
          if (content.classList.contains("ag-is-dropdownOpen")) {
            if (btn.classList.contains("ag-is-searchOpen")) {
              btn.classList.remove("ag-is-searchOpen");
            }
            btn.classList.remove("i-after-arrow-up");
            btn.classList.add("i-after-arrow-down");
            content.classList.remove("ag-is-dropdownOpen");
            btn.classList.contains("ag-js-filterBtnDropdown") &&
              content.classList.add("ag-is-hidden");
          } else {
            if (!btn.classList.contains("ag-is-searchOpen")) {
              btn.classList.add("ag-is-searchOpen");
              // It's only add if is in pages of expositions
              if (asideMenu) {
                asideMenu.classList.add("ag-is-menu-aside-close");
              }
            }
            btn.classList.remove("i-after-arrow-down");
            btn.classList.add("i-after-arrow-up");
            content.classList.add("ag-is-dropdownOpen");
            btn.classList.contains("ag-js-filterBtnDropdown") &&
              content.classList.remove("ag-is-hidden");
          }
        }
      }
    });
  }
})();
