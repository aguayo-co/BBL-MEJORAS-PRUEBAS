document.addEventListener("DOMContentLoaded", function() {
  // cookies functions
  require("./utils/cookies");

  // accessibility JS
  require("./components/accessibility.js");

  // animations JS
  // require("./components/animate.js");

  //- add search to multiple select fields
  require("./components/choices_select_search_filter_init");

  //- c01_search
  require("./components/c01_search");

  //- Componente c09_menu
  require("./components/c09_menu.js");

  //- Block b28_list-button
  require("./components/b28_list-button.js");

  //- Componente c06_dropdown.
  require("./components/c06_dropdown");

  //- Componente c11_modal.
  require("./components/c11_modal");

  // Upload files
  require("./components/uploadFiles");

  // Alerts
  require("./components/alert");

  // c14_rating
  require("./components/c14_rating");

  // collection
  require("./components/collection");

  // collection
  require("./components/collectionsGroup");

  // Lógica compartir, redes sociales, copiar links ...
  require("./components/share");

  // Iframes
  require("./components/iframes");

  //- Componente c06-carousel.
  setTimeout(() => {
    require("./components/c07-slider.js");
  }, 300);

  // Filter JS
  require("./components/filter");

  // Validaciones
  require("./components/formValidate");

  // Lógica switch crear colección
  require("./components/b16_switch");

  // Lógica tooltip de ayuda
  require("./components/c15_tooltip");

  // Lógica botón de scroll down
  require("./components/scroll_down");

  // Componente cloud terms
  require("./components/c24_cloud-terms.js");

  // Nav element current
  require("./components/element_menu_current");

  // Cropper
  require("./components/c29_cropper");

  // Loader
  require("./components/c30_loader.js");

  // Tabs
  require("./components/tabs");

  //Collapsible
  require("./components/collapsible.js");

  //Hero Scroll Down
  require("./components/hero_btn.js");
});
