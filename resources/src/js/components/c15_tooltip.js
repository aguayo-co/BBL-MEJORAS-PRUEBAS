// Elementos del DOM
function getTooltipElement() {
  return document.getElementsByClassName("ag-js-tooltipButton");
}

function actionBtnTooltip() {
  const btnsTooltip = Array.from(getTooltipElement());

  btnsTooltip.forEach(btnTooltip => {
    btnTooltip.addEventListener("click", function() {
      const maskTooltip = btnTooltip.closest(".ag-c-tooltip");
      // Si la caja del tooltip contiene la clase ag-is-tipHidden
      // se remueve, si no la agrega
      maskTooltip.classList.toggle("ag-is-tipHidden");

      if (maskTooltip.parentElement.nextElementSibling != null) {
        maskTooltip.parentElement.nextElementSibling.classList.toggle(
          "js-tootlipZindex"
        );
      }
    });
  });
}

actionBtnTooltip();
