// Función mostrar imagen al añadirla por un input file
const addImage = function(e) {
  const inputFile = e.target,
    file = inputFile.files[0],
    imageType = /image.*/,
    container = inputFile.closest(".ag-js-formfieldUploadImg"),
    img = container.getElementsByClassName("ag-js-imageUploaded")[0],
    name = container.getElementsByClassName("ag-js-imageUploadedName")[0],
    containerImgShow = container.getElementsByClassName("ag-js-fileUpload")[0];
  // Verifica si se eligió una imagen
  if (file) {
    // Verifica que sea un tipo de imagen valido
    if (!file.type.match(imageType)) return;

    const reader = new FileReader();
    reader.onload = function(e) {
      // Colocamos la imagen y el nombre en el html
      img.src = e.target.result;
      img.title = file.name;
      name.innerText = file.name;
      containerImgShow.style.display = "flex";
    };
    // Leemos el archivo de imagen
    reader.readAsDataURL(file);
  } else {
    // Si no eligió ninguna imagen (cancelar) se limpia toda la información y el html.
    img.src = "";
    img.title = "";
    name.innerText = "";
    containerImgShow.style.display = "none";
  }
};

// Al input con nombre 'Avatar' le asignamos que ejecute la función de addImage al detectar un cambio
document.getElementsByName("avatar")[0] &&
  document.getElementsByName("avatar")[0].addEventListener("change", addImage);

document.getElementsByName("image")[0] &&
  document.getElementsByName("image")[0].addEventListener("change", addImage);
