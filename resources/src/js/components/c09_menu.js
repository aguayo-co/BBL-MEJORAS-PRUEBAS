(function menu() {
  const btnMenu = document.getElementsByClassName("ag-js-btnOpenMenu")[0];
  const btnBackMenu = document.getElementsByClassName("ag-js-btnBack")[0];
  const contentMenu = document.getElementsByClassName("ag-js-subMenu")[0];
  // aside menu for expositions
  const asideMenu = document.querySelector(".ag-js-asideMenuNav");
  if (!btnMenu) {
    return;
  }
  const menuFunc = function() {
    const searchDropdownMobile = document.getElementsByClassName(
      "ag-js-searchDropdownMobile"
    )[0];
    const searchBtnMobile = document.getElementsByClassName(
      "ag-js-searchBtnMobile"
    )[0];

    searchDropdownMobile &&
      searchDropdownMobile.classList.remove("ag-is-dropdownOpen");
    searchBtnMobile && searchBtnMobile.classList.remove("ag-is-searchOpen");

    if (contentMenu.classList.contains("ag-is-menu_showmobile")) {
      contentMenu.classList.remove("ag-is-menu_showmobile");
      contentMenu.classList.add("ag-is-menu_hidemobile");
      btnMenu.classList.remove("ag-is-active");
    } else {
      btnMenu.classList.remove("ag-is-menu_hidemobile");
      contentMenu.classList.add("ag-is-menu_showmobile");
      btnMenu.classList.add("ag-is-active");
      // It's only add if is in pages of expositions
      if (asideMenu) {
        asideMenu.classList.add("ag-is-menu-aside-close");
      }
    }
  };
  btnMenu.addEventListener("click", menuFunc);
  btnBackMenu.addEventListener("click", menuFunc);

  // Lógica agrega clase .ag-has-menu__focus al hacer presionar Tab apuntando al menu.
  document.addEventListener("keyup", function(e) {
    if (event.keyCode == 9) {
      const target = e.target;
      const hasClassTab = Array.from(
        document.getElementsByClassName("ag-has-menu__focus")
      );
      const hasHeaderClassTab = Array.from(
        document.getElementsByClassName("ag-has-accesibilityopen")
      );
      const menuChipFocus = Array.from(
        document.getElementsByClassName("ag-has-menu-chip__focus")
      );

      hasClassTab.forEach(item => {
        item.classList.remove("ag-has-menu__focus");
      });
      hasHeaderClassTab.forEach(item => {
        item.classList.remove("ag-has-accesibilityopen");
      });
      menuChipFocus.forEach(item => {
        item.classList.remove("ag-has-menu-chip__focus");
      });

      if (target.classList.contains("ag-js-menuSublistItem")) {
        const menuListItem = target.closest(".ag-js-menuListItem");
        menuListItem.classList.add("ag-has-menu__focus");
        menuListItem.classList.add("ag-has-menu-chip__focus");
        menuListItem.classList.remove("ag-has-accesibilityopen");
      }

      target.closest(".ag-js-menuListHeader") &&
        target
          .closest(".ag-js-menuListHeader")
          .classList.add("ag-has-accesibilityopen");

      if (target.classList.contains("ag-js-accesibilityTop")) {
        document
          .querySelector("header.ag-is-menu_fixed")
          .classList.add("ag-has-accesibilitytop");
      } else {
        document
          .querySelector("header.ag-is-menu_fixed")
          .classList.remove("ag-has-accesibilitytop");
      }
    }
  });

  const accesibilityTop = Array.from(
    document.getElementsByClassName("ag-js-accesibilityTop")
  );
  const headerFixed = document.querySelector("header.ag-is-menu_fixed");
  accesibilityTop.forEach(elem => {
    elem.addEventListener("focusout", function() {
      headerFixed.classList.remove("ag-has-accesibilitytop");
    });
  });

  // Toggle aside menu by buttons
  const asideMenus = document.getElementsByClassName("ag-js-asideMenuNav");
  asideMenus.forEach(asideMenu => {
    const toggleMenu = function() {
      asideMenu.classList.toggle("ag-is-menu-aside-close");
      closeOtherAsideMenu();
    };
    asideMenu
      .getElementsByClassName("ag-c-menu-aside__main-button")
      .forEach(btn => {
        btn.addEventListener("click", toggleMenu);
      });
    asideMenu.getElementsByClassName("ag-is-menu-aside__close").forEach(btn => {
      btn.addEventListener("click", toggleMenu);
    });
  });

  const closeOtherAsideMenu = function() {
    document
      .getElementsByClassName("ag-js-asideFiltersMenu")
      .forEach(otherAsideMenu => {
        otherAsideMenu.classList.add("ag-is-filter-aside-close");
      });
  };
})();
