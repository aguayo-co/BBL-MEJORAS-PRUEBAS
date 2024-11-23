function buildExpandingFormset(prefix, opts) {
  if (!opts) {
    opts = {};
  }

  var addButton = $("#" + prefix + "-ADD");
  var formContainer = $("#" + prefix + "-FORMS");
  var totalFormsInput = $("#" + prefix + "-TOTAL_FORMS");
  var formCount = parseInt(totalFormsInput.val(), 10);

  if (opts.onInit) {
    for (var i = 0; i < formCount; i++) {
      opts.onInit(i);
    }
  }

  var emptyFormTemplate = document.getElementById(
    prefix + "-EMPTY_FORM_TEMPLATE"
  );
  if (emptyFormTemplate.innerText) {
    emptyFormTemplate = emptyFormTemplate.innerText;
  } else if (emptyFormTemplate.textContent) {
    emptyFormTemplate = emptyFormTemplate.textContent;
  }

  /* MAP MILESTONE */
  //Suscribir al broadcastChannel si no lo ha hecho
  const broadcastChannel = new BroadcastChannel("add_child");
  //Llenar datos del formulario cuando se recibe un mensaje
  broadcastChannel.onmessage = function(ev) {
    console.log("Formulario Hijo Recibido");
    // Llenar el ultimo formulario con los datos recibidos en el mensaje
    if (ev.data.title) {
      let last_child = $(`#${prefix}-FORMS`)
        .children()
        .last();
      last_child.find("div").remove();
      last_child.append(
        `<div class="instance-selector-widget__display__title-wrap">${ev.data.title}</div>`
      );
      last_child.append(`<div class="instance-selector-widget__actions">
                        <a href="${ev.data.url}" class="edit-link button button-small button-secondary instance-selector-widget__actions__edit js-instance-selector-widget-edit" target="_blank">Editar Hito</a>
                       </div>`);
    }
  };

  //Obtener la URL donde se crearan los MapMilestones
  const addNewUrl = document.getElementById(prefix + "-ADD-NEW-URL");

  addButton.on("click", function() {
    if (addButton.hasClass("disabled")) return false;

    if (addButton.hasClass("new-tab")) {
      //Abrir el formulario hijo en una nueva ventana
      window.open(addNewUrl.text, "_blank");
    }
    var newFormHtml = emptyFormTemplate
      .replace(/__prefix__/g, formCount)
      .replace(/<-(-*)\/script>/g, "<$1/script>");
    formContainer.append(newFormHtml);
    if (opts.onAdd) opts.onAdd(formCount);
    if (opts.onInit) opts.onInit(formCount);

    formCount++;
    totalFormsInput.val(formCount);
  });
}
