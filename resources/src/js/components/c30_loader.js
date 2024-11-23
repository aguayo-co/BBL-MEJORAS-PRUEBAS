function hideLoader() {
  window.addEventListener("load", () => {
    const targetLoad = document.querySelector(".js-loader-target");

    if (targetLoad) {
      setTimeout(() => {
        targetLoad.classList.remove("ag-is-modal_visible");
      }, 500);
    }
  });
}

hideLoader();
