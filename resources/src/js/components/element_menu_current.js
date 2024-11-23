class MenuCurrent {
  constructor(navigationLinks, classCurrentLink) {
    this.navigationLinks = Array.from(
      document.querySelectorAll(navigationLinks)
    );
    this.classCurrentLink = classCurrentLink;
    this.URLCurrent = window.location;
    this.navigationSubLinks = "";
    this.addClassCurrent();
  }

  addClassCurrent() {
    this.navigationLinks.map(linkCurrent => {
      if (this.URLCurrent.href == linkCurrent.href) {
        linkCurrent.classList.add(this.classCurrentLink);
      } else if (linkCurrent.classList.contains("ag-js-dropdownBtn")) {
        this.navigationSubLinks = Array.from(
          linkCurrent.nextElementSibling.querySelectorAll(".ag-c-menu__link")
        );
        this.navigationSubLinks.map(subLinkCurrent => {
          if (
            subLinkCurrent.href == this.URLCurrent.href ||
            this.URLCurrent.pathname == subLinkCurrent.getAttribute("data-href")
          ) {
            linkCurrent.classList.add(this.classCurrentLink);
            subLinkCurrent.classList.add("ag-has-submenu-current");
          }
        });
      }
    });
  }
}

new MenuCurrent(".ag-c-menu__head-link", "ag-has-menu-current");
