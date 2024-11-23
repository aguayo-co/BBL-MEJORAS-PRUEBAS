function focusElementsForAccessibility(element, elementIsIterable = false) {
  if (!elementIsIterable) {
    element = [element];
  }
  element.forEach(el => {
    setTimeout(() => {
      el.focus();
    }, 50);
  });
}

// The aside element of the document is being brought in
function elemAsideDepth() {
  return document.querySelector(".ag-js-asideDepth");
}

function closeModal(modal, openModalElement) {
  modal.classList.remove("ag-is-modal_visible");
  document.body.classList.remove("ag-is-overflow");

  // When class is removed into element the aside is move to front
  if (elemAsideDepth()) {
    elemAsideDepth().classList.remove("ag-is-aside_depth");
  }

  focusElementsForAccessibility(openModalElement);
}

function openModal(target) {
  const modalBind = target.getAttribute("data-modal");
  const modal = document.querySelector(
    '.ag-js-modal[data-modal="' + modalBind + '"]'
  );
  modal.classList.add("ag-is-modal_visible");
  document.body.classList.add("ag-is-overflow");

  // When class is append into element the aside is move to back
  if (elemAsideDepth()) {
    elemAsideDepth().classList.add("ag-is-aside_depth");
  }

  focusElementsForAccessibility(
    modal.getElementsByClassName("ag-js-modalContent"),
    true
  );

  const modalCloseButtons = modal.getElementsByClassName("ag-js-modalClose");
  modalCloseButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      closeModal(modal, target);
    });
    if (btn.innerHTML != "Cancelar") {
      btn.addEventListener("keydown", e => {
        closeModal(modal, target);
      });
    }
  });
}

document.addEventListener("click", function(e) {
  if (
    e.target &&
    ["BUTTON", "A"].includes(e.target.tagName) &&
    e.target.hasAttribute("data-modal")
  ) {
    openModal(e.target);
  }

  if (
    e.target &&
    ["LI"].includes(e.target.tagName) &&
    e.target.classList.contains("ag-js-videoSlider")
  ) {
    openModal(e.target);
  }

  if (
    e.target &&
    ["IMG"].includes(e.target.tagName) &&
    e.target.classList.contains("leaflet-marker-icon")
  ) {
    openModal(e.target);
  }
});

export { openModal };
