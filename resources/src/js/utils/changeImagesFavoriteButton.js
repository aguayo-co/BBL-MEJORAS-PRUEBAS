export function changeImagesButton(btn, numberData) {
  const buttonIconFavorite = btn.querySelector(".ag-js-btnIconChange");
  const buttonTextFavorite = btn.querySelector(".ag-js-btnTextChange");

  let srcString = buttonIconFavorite.getAttribute("src");
  if (buttonIconFavorite) {
    if (numberData == 1) {
      let stateButton = srcString.replace("_inactive_", "_active_");
      buttonIconFavorite.setAttribute("src", stateButton);
      buttonTextFavorite.textContent = "Eliminar de favoritos";
    }
    if (numberData == 0) {
      let stateButton = srcString.replace("_active_", "_inactive_");
      buttonIconFavorite.setAttribute("src", stateButton);
      buttonTextFavorite.textContent = "Agregar a favoritos";
    }
  }
}
