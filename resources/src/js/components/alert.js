function setAlerts() {
  // Selector de los botones de las alertas
  const alertsBtnClose = Array.from(
    document.getElementsByClassName("ag-js-messageClose")
  );
  // Verifica si existe al menos un botón de cerrar alerta para agregarles el evento
  if (alertsBtnClose[0]) {
    // Agrega evento de cerrar al botón cerrar (X) de las alertas
    alertsBtnClose.forEach(x => {
      const alertElement = x.closest(".js-messagesItem");
      const waitingTimeToDisplay = 1000;
      const leftTimeToDisplay = 15000;
      // Muestra la alerta 1 segundo (valor guardado en la variable waitingTimeToDisplay) después de cargar la pagina
      setTimeout(() => {
        alertElement.classList.remove("ag-is-messageClose");
        alertElement.classList.add("ag-has-messageOpen");

        // Después de un tiempo se retira de escena el mensaje
        setTimeout(() => {
          alertElement.classList.add("ag-is-messageClose");
          alertElement.classList.remove("ag-has-messageOpen");
        }, leftTimeToDisplay);
      }, waitingTimeToDisplay);

      // Al hacer click en el botón cerrar agrega la clase ag-is-messageClose la cual contiene las animaciones y los estilos para cerrar la alerta
      x.addEventListener("click", function() {
        alertElement.classList.add("ag-has-messageClose");
      });
    });
  }
}

setAlerts();

export default setAlerts;
