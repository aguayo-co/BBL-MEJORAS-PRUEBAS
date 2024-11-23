import $ from "jquery";
import "../vendor/typeahead.jquery.js";
import axios from "axios";

/**
 * @function templateSuggetion Template para renderizar sugerencias y lista de los colaboradores y/o invitados;
 * @param {Array} val : Listado de información con el id, avatar y nombre de la sugerencia
 * @param {'toSelect' 'select' 'delete'} state : Estado del botón, opciones= 'toSelect' 'select' 'delete'
 */
const templateSuggetion = (val, state = "toSelect") => {
  const id = val.id;
  let text = "",
    classList = "";
  switch (state) {
    case "toSelect": // Estado sin seleccionar, cambia el texto del botón a "Seleccionar")
      text = "Seleccionar";
      break;
    case "select": // Estado seleccionado, cambia el texto del botón a "Seleccionado" y agrega la clase 'ag-o-btn_outline')
      text = "Seleccionado";
      classList = "ag-o-btn_outline";
      break;
    case "delete":
      text = "Eliminar"; // Estado Eliminar, cambia el texto del botón a "Eliminar" y agrega la clase 'ag-o-btn_outline' y 'ag-js-inviteDeletetBtn' esta clase sirve para la funcionalidad de eliminar)
      classList = "ag-js-inviteDeletetBtn ag-o-btn_outline";
      break;
    default:
      break;
  }
  return `
    <div class="ag-list__item ag-js-inviteBox" id="${id}" tabindex="0">
        <div class="ag-list__row ag-list__row_small">
            <div class="ag-list__visual">
                <figure class="ag-chip__avatar">
                    ${
                      val.avatar
                        ? `<img class="ag-chip__img" src="${val.avatar}" alt="Usuario">`
                        : val.initials
                    }
                </figure>
            </div>
            <div class="ag-list__content">${val.name}</div>
            <div class="ag-list__actions">
                <button class="ag-o-btn ${classList}" name="${id}" type="button" tabindex="0">
                    ${text}
                    <span class="ag-is-visuallyhidden">${val.name}</span>
                </button>
            </div>
        </div>
    </div>
    `;
};

// Configuración typeahead de input "Invitar colaborador"
$("#invite-collaborators").typeahead(
  {
    hint: false,
    highlight: true,
    minLength: 1
  },
  {
    name: "states",
    source: function(query, cb, as) {
      axios.get("?search_text=" + query).then(function(response) {
        const values = Object.keys(response.data).map(function(e) {
          return response.data[e];
        });
        as(values); // Se hace la petición y con as() se colocan los datos a typeahead
      });
    },
    display: "name",
    templates: {
      empty: "",
      suggestion: function(val) {
        const inputCollaborators = document.querySelector(
          'input[name="collaborators"]'
        );
        const id = val.id;

        let values = inputCollaborators.value
          ? inputCollaborators.value.split(",")
          : []; // Traemos el valor del input "collaborators"  y lo convertimos a un array de todos los id seleccionados.
        values = values.map(x => x * 1); // Pasamos todos los valores del arreglo de string a enteros

        // Renderiza lista de sugerencias en el buscador de invitar colaborador
        if (values.includes(id)) {
          return templateSuggetion(val, "select"); // Si el id de la sugerencia existe en el arreglo values (o sea ya esta seleccionado) se enviá el template con estado 'select'.
        } else {
          return templateSuggetion(val, "toSelect"); // Si el id de la sugerencia no existe en el arreglo values (o sea no esta seleccionado) se enviá el template con estado 'toSelect'.
        }
      }
    }
  }
);

// Funcionalidad Añadir colaborador a lista para invitar
$("#invite-collaborators").bind("typeahead:select", function(_e, suggestion) {
  const inputCollaborators = document.querySelector(
    'input[name="collaborators"]'
  );
  const id = suggestion.id;
  let values = inputCollaborators.value
    ? inputCollaborators.value.split(",")
    : []; // Traemos el valor del input "collaborators"  y lo convertimos a un array de todos los id seleccionados.

  values = values.map(x => x * 1); // Pasamos todos los valores del arreglo de string a enteros

  if (!values.includes(id)) {
    // Verifica que el colaborador escogido no este ya en la lista de invitados
    // Agrega el nuevo colaborador al input "collaborators"
    values.push(id);
    inputCollaborators.value = values.join(",");

    const collaboratorsList = document.querySelector(
      ".ag-js-collaboratorsInvitedBox"
    );
    if (values.length == 1) {
      // Al seleccionar el primer usuario para invitar se elimina el mensaje 'Aún no tienes personas a invitar.'.
      collaboratorsList.innerHTML = "";
    }

    // Agrega el elemento (HTML) del usuario seleccionado a la lista de invitados.
    collaboratorsList.innerHTML += templateSuggetion(suggestion, "delete");

    $(this).typeahead("val", ""); // Deja vacío el buscador de usuarios
  } else {
    $(this).typeahead("val", ""); // Deja vacío el buscador de usuarios
  }
});

// Funcionalidad eliminar colaborador de lista para invitar
document.addEventListener("click", function(e) {
  if (!e.target || !e.target.classList.contains("ag-js-inviteDeletetBtn")) {
    return;
  }

  const btn = e.target;
  const elementBox = btn.closest(".ag-js-inviteBox");
  const inputCollaborators = document.querySelector(
    'input[name="collaborators"]'
  );

  let values = inputCollaborators.value
    ? inputCollaborators.value.split(",")
    : []; // Traemos el valor del input "collaborators"  y lo convertimos a un array de todos los id seleccionados.

  // Se elimina el id (del colaborador que se desea quitar de la lista de invitados) del input "collaborators"
  values.splice(values.indexOf(btn.name), 1);
  inputCollaborators.value = values;

  $("#invite-collaborators").typeahead("val", ""); // Se deja vació el buscador de colaboradores para evitar errores de estado con el colaborador eliminado.

  elementBox.remove(); // Se elimina el elemento (HTML) de la lista de invitados.

  if (values.length == 0) {
    // Si no hay ningún usuario seleccionado para invitar, se muestra el mensaje 'Aún no tienes personas a invitar.'.
    document.querySelector(".ag-js-collaboratorsInvitedBox").innerHTML = `
        <li class="ag-list__item">
            <div class="ag-list__row ag-list__row_small" tabindex="0">
            Aún no tienes personas a invitar.
            </div>
        </li>`;
  }
});

//Buscador invitar colaborador
//Al hacer click en botón buscar abre las sugerencias de los usuarios
const searchCollaboratorBtn = document.getElementsByClassName(
  "ag-js-searchCollaboratorBtn"
)[0];
if (searchCollaboratorBtn) {
  searchCollaboratorBtn.addEventListener("click", function(e) {
    e.preventDefault();
    $("#invite-collaborators").typeahead("open");
  });
}

// Tooltip alerta buscador invitar
const inviteForm = document.getElementById("invite-form");
if (inviteForm) {
  const searchCollaboratorInput = inviteForm.querySelector(
    "#invite-collaborators"
  );
  const tooltipSearch = inviteForm.getElementsByClassName("ag-js-tip")[0];
  const searchCollaboratorBtn = inviteForm.getElementsByClassName(
    "ag-js-searchCollaboratorBtn"
  )[0];

  // Si al hacer submit no hay nada escrito aparece el tooltip de alerta.
  searchCollaboratorBtn.addEventListener("click", function(ev) {
    ev.preventDefault();

    if (searchCollaboratorInput.value.length === 0) {
      if (tooltipSearch) {
        tooltipSearch.removeAttribute("hidden");
        tooltipSearch.classList.add("ag-is-show");
      }

      inviteForm
        .getElementsByClassName("ag-js-searchCollaboratorInput")[0]
        .classList.add("ag-is-warning");
    }
  });

  // Al escribir algo en el search desaparece el tooltip de alerta.
  searchCollaboratorInput.addEventListener("input", function(ev) {
    ev.preventDefault();

    if (searchCollaboratorInput.value.length > 0) {
      if (tooltipSearch) {
        tooltipSearch.setAttribute("hidden", "hidden");
        tooltipSearch.classList.remove("ag-is-show");
      }

      inviteForm
        .getElementsByClassName("ag-js-searchCollaboratorInput")[0]
        .classList.remove("ag-is-warning");
    }
  });
}

// Cierra sugerencias buscador colaboradores al dar click afuera
document.addEventListener("mouseup", function(e) {
  const searchCollaboratorInput = document.getElementsByClassName(
    "ag-js-searchCollaboratorInput"
  )[0];
  if (searchCollaboratorInput && !searchCollaboratorInput.contains(e.target)) {
    $("#invite-collaborators").typeahead("close");
    const tooltipSearch = inviteForm.getElementsByClassName("ag-js-tip")[0];
    if (tooltipSearch) {
      tooltipSearch.setAttribute("hidden", "hidden");
      tooltipSearch.classList.remove("ag-is-show");
    }
    inviteForm
      .getElementsByClassName("ag-js-searchCollaboratorInput")[0]
      .classList.remove("ag-is-warning");
  }
});
