function initButtonList() {
  /** The element with hidden list and inside with a list of dynamic buttons. **/
  const handlerButtonList = document.querySelectorAll(
    ".ag-js-actionButtonList"
  );
  // let isMouseDown = false;

  handlerButtonList.forEach(currentButton => {
    const parentList = currentButton.closest(".ag-js-buttonList");
    // const elementList = currentButton.nextElementSibling;

    currentButton.addEventListener("click", function() {
      if (parentList.classList.contains("ag-is-list-button_open")) {
        parentList.classList.remove("ag-is-list-button_open");
      } else {
        handlerButtonList.forEach(siblingsList => {
          parentSiblings = siblingsList.closest(".ag-js-buttonList");
          if (parentSiblings.classList.contains("ag-is-list-button_open")) {
            parentSiblings.classList.remove("ag-is-list-button_open");
          }
        });
        parentList.classList.add("ag-is-list-button_open");
      }
      // event.preventDefault();
      // elementList.tabIndex = 0;
      // elementList.focus();
      // parentList.classList.toggle("ag-is-list-button_open");
    });

    // elementList.addEventListener("mousedown", function() {
    //   isMouseDown = true;
    // });

    // elementList.addEventListener("mouseup", function() {
    //   isMouseDown = false;
    // });

    // elementList.addEventListener("mouseleave", function() {
    //   isMouseDown = false;
    // });

    // elementList.addEventListener(
    //   "blur",
    //   function() {
    //     if (!isMouseDown) {
    //       parentList.classList.remove("ag-is-list-button_open");
    //     }
    //   },
    //   true
    // );
  });
}

function hiddeAllElementsList() {
  const handlerButtonList = document.querySelectorAll(
    ".ag-js-actionButtonList"
  );

  window.addEventListener("click", e => {
    if (!e.target.closest(".ag-js-buttonList")) {
      handlerButtonList.forEach(listButton => {
        listButton
          .closest(".ag-js-buttonList")
          .classList.remove("ag-is-list-button_open");
      });
    }
  });
}

hiddeAllElementsList();
initButtonList();
