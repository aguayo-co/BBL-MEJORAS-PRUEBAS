const modal = $(`
            <div class="modal fade instance-selector-widget-modal" tabindex="-1" role="dialog" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content instance-selector-widget-modal__content">
                        <button type="button" class="button close icon text-replace icon-cross" data-dismiss="modal" aria-hidden="true">&times;</button>
                        <div class="modal-body instance-selector-widget-modal__body">
                        <!--TODO esto debe quedar bonito -->
                            Se han guardado los cambios, puede cerrar esta ventana                     
                        </div>
                    </div>
                </div>
            </div>
        `);

$(document).ready(function() {
  //Hide Timeline Id
  $("#id_timeline")
    .closest("li")
    .hide();
  // Remove any previous modals
  $("body > .modal").remove();
  // Add modal
  $("body").append(modal);
});

$(document).on(
  "click",
  "button.button.action-save.button-longrunning",
  function(e) {
    var button = $(this);
    var form = button.closest("form").get(0);

    //Suscribir al broadcastChannel si no lo ha hecho
    const broadcastChannel = new BroadcastChannel("add_child");

    // Deshabilita el submit, pues no queremos enviar los datos, pero queremos las animaciones
    e.preventDefault();

    //Clean Errors
    $(".error-message").remove();

    // Ajax Submit
    $.post($(form).attr("action"), $(form).serializeArray(), function(data) {
      //Post Message with Id, Name
      broadcastChannel.postMessage(data);
      broadcastChannel.close();
      window.close();
    }).fail(function(errors) {
      $.each(errors.responseJSON, function(index, error) {
        $(`[name="${index}"]`).after(
          `<p id="error" class="error-message"><span>${error[0]}</span></p>`
        );
      });
    });
  }
);

function show_modal() {
  modal.modal("show");
}

function hide_modal() {
  modal.modal("hide");
  window.close();
}
