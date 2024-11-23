// Se obtienen elementos del DOM
const switchPublic = document.getElementById("id_public");
const switchCollaborative = document.getElementById("id_collaborative");

// Evento change que verifica si el switch esta check o uncheck
if (switchPublic) {
  switchPublic.addEventListener("change", validateCheckbox);
}

//  Onload para que el switch collaborative este disabled
//  al cargar la página
window.onload = () => {
  validateCheckbox();
};

function validateCheckbox() {
  if (switchPublic) {
    let check = switchPublic.checked;
    if (!check) {
      switchCollaborative.setAttribute("disabled", "");

      if (switchCollaborative.checked) {
        switchCollaborative.checked = false;
      }
    } else {
      switchCollaborative.removeAttribute("disabled");
    }
  }
}
