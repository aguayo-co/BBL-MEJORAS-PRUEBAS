let lastKnownScrollPosition = 0;
const barMenu = document.querySelector(".ag-js-menuAsideControl");
function addClassOpenMenu() {
  barMenu.classList.add("ag-is-menu-aside-open");
}

function removeClassForCloseMenu() {
  barMenu.classList.remove("ag-is-menu-aside-open");
}

function appearToMenu(callback, refresh = 15000) {
  if (!callback || typeof callback !== "function") return;
  let isScroll;
  window.addEventListener(
    "scroll",
    function() {
      addClassOpenMenu();
      window.clearTimeout(isScroll);
      isScroll = setTimeout(callback, refresh);
      lastKnownScrollPosition = window.scrollY;
      if (lastKnownScrollPosition === 0) {
        removeClassForCloseMenu();
      }
    },
    false
  );
}

appearToMenu(function() {
  removeClassForCloseMenu();
});
