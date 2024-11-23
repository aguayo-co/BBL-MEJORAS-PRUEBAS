const openIframeModalButtons = document.querySelectorAll(
  ".ag-js-collection_iframe_open_btn"
);

for (let i = 0; i < openIframeModalButtons.length; i++) {
  const btn = openIframeModalButtons[i];
  const iframeName = btn.dataset.for;
  const iframeSrc = btn.dataset.iframeSrc;
  btn.addEventListener("click", () => {
    const iframe = document.querySelector(`iframe[data-name='${iframeName}']`);
    iframe.setAttribute("src", iframeSrc);
    iframe.addEventListener("load", () => {
      iframe.parentElement
        .querySelector(".ag-js-iframe-loader")
        .classList.add("ag-is-spinner_hide");
    });
  });
}
