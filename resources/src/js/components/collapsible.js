class Collapsible {
  constructor({ element }) {
    this.element = element;
    this.options =
      element.dataset && JSON.parse(element.dataset.jsCollapsibleOptions);
    this.items = this.element.children;
    this.control = [];
    this.targets = [];
    for (let i = 0; i < this.items.length; i++) {
      const control = this.items[i].children[0];
      const target = this.items[i].children[1];
      this.control.push(control);
      this.targets.push(target);
    }
    this.openedClass = "is-collapsible-open";
    this.contentWrapperClass = "js-collapsible-wrapper";
    this.hanldeTitleClick = this.hanldeTitleClick.bind(this);
    this.init();
  }

  init() {
    this.control.forEach(element => {
      element.addEventListener("click", () => {
        this.hanldeTitleClick(element);
      });
    });
    this.setInitialStyleToitems();
    window.addEventListener("resize", this.handleWindowResize.bind(this));
  }

  setInitialStyleToitems() {
    this.targets.forEach(target => {
      const maxHeight = target.clientHeight;
      target.setAttribute("data-maxHeight", maxHeight);
    });
    const { firstElemenVisible } = this.options;
    if (firstElemenVisible) {
      this.targets.forEach((target, idx) => {
        if (idx > 0) {
          this.hideTarget(target);
        } else {
          target.parentElement.classList.add(this.openedClass);
          this.showtarget(target);
        }
      });
    } else {
      this.targets.forEach(target => {
        this.hideTarget(target);
      });
    }
  }

  showtarget(target) {
    const contentWrapper = target.querySelector(`.${this.contentWrapperClass}`);
    target.style.maxHeight = contentWrapper.clientHeight + "px";
  }

  hideTarget(target) {
    target.style.maxHeight = 0;
  }

  hanldeTitleClick(element) {
    const target = element.nextElementSibling;
    const parent = element.parentElement;
    const iOpened = parent.classList.contains(this.openedClass);
    if (!iOpened) {
      for (let i = 0; i < this.items.length; i++) {
        const item = this.items[i];
        item.classList.remove(this.openedClass);
        const target = item.querySelectorAll(".js-collapsible-target")[0];
        this.hideTarget(target);
      }
      parent.classList.add(this.openedClass);
      this.showtarget(target);
    } else {
      parent.classList.remove(this.openedClass);
      this.hideTarget(target);
    }
  }

  handleWindowResize() {
    const openedElements = document.getElementsByClassName(this.openedClass);
    Array.from(openedElements).forEach(item => {
      const target = item.children[1];
      const contentWrapper = target.querySelector(
        `.${this.contentWrapperClass}`
      );
      target.setAttribute("data-maxHeight", contentWrapper.clientHeight + "px");
      target.style.maxHeight = contentWrapper.clientHeight + "px";
    });
  }
}

const collapsible = document.querySelectorAll(".js-collapsible");

collapsible.forEach(item => {
  new Collapsible({
    element: item
  });
});
