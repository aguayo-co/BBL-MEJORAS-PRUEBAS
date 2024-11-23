// Función recarga iframe al presionar botón vinculado
const btnOpenModalIframe = Array.from(
  document.getElementsByClassName("ag-js-reloadIframe")
);
btnOpenModalIframe.forEach(btn => {
  const agFor = btn.getAttribute("data-for");
  btn.addEventListener("click", function(e) {
    const iframe = document.querySelector(`iframe[data-name='${agFor}']`);
    iframe.parentElement
      .querySelector(".ag-js-iframe-loader")
      .classList.remove("ag-is-spinner_hide");
    // iframe.contentDocument.location.reload(true);
  });
});
