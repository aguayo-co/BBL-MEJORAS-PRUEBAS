export function addDeleteListItemEventsListeners(
  openModalBtnClassName,
  modalBtnClassName
) {
  const openModalButtons = document.querySelectorAll(
    `.${openModalBtnClassName}`
  );
  const modalButtons = document.querySelectorAll(`.${modalBtnClassName}`);
  if (openModalButtons.length) {
    openModalButtons.forEach(openModalBtn => {
      openModalBtn.addEventListener("click", function() {
        modalButtons.forEach(modalBtn => (modalBtn.value = openModalBtn.value));
      });
    });
  }
}

export function addDeleteDetailPageObjectEventsListeners(modalBtnClassName) {
  const modalButtons = document.querySelectorAll(`.${modalBtnClassName}`);
  if (modalButtons.length) {
    modalButtons.forEach(modalBtn => {
      modalBtn.addEventListener("click", function() {
        const inputDelete = document.getElementsByClassName("ag-js-delete")[0];
        inputDelete.removeAttribute("hidden");
        inputDelete.setAttribute("name", "delete");
        inputDelete.form.submit();
      });
    });
  }
}
