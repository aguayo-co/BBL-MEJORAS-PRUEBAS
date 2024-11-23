import $ from "jquery";
import "../vendor/typeahead.jquery.js";
import axios from "axios";

export const getUsersListValues = userListInput => {
  let values = userListInput.value ? userListInput.value.split(",") : []; // Traemos el valor del input con la lista de usuarios  y lo convertimos a un array de todos los id seleccionados.
  values = values.map(x => x * 1); // Pasamos todos los valores del arreglo de string a enteros
  return values;
};

/**
 * @function templateSuggetion Template para renderizar sugerencias y lista de los usuarios;
 * @param {Array} val : Listado de información con el id, avatar y nombre de la sugerencia
 * @param {'toSelect', 'select', 'delete'} state : Estado del botón, opciones= 'toSelect' 'select' 'delete'
 */
export const templateSuggestion = (val, state = "toSelect") => {
  const id = val.id;
  let text = "",
    classList = "";
  switch (state) {
    case "toSelect": // Estado sin seleccionar, cambia el texto del botón a "Seleccionar")
      text = "Seleccionar";
      classList = "ag-js-userSelectBtn";
      break;
    case "select": // Estado seleccionado, cambia el texto del botón a "Seleccionado" y agrega la clase 'ag-o-btn_outline')
      text = "Seleccionado";
      classList = "ag-o-btn_outline";
      break;
    case "delete":
      text = "Eliminar"; // Estado Eliminar, cambia el texto del botón a "Eliminar" y agrega la clase 'ag-o-btn_outline' y 'ag-js-userDeletetBtn' esta clase sirve para la funcionalidad de eliminar)
      classList = "ag-js-userDeletetBtn ag-o-btn_outline";
      break;
    case "shared":
      text = "Compartido"; // Estado Compartido
      classList = "ag-js-userSharedBtn ag-o-btn_outline";
      break;
    default:
      break;
  }
  return `
    <div class="ag-list__item ag-js-inviteBox" id="${id}" tabindex="0">
        <div class="ag-list__row">
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

export function initUserSearchSuggestions(
  searchInputTypeAheadSelector,
  userListInput,
  requestForm,
  searchUserInputWrapper,
  searchUserInput,
  searchUserBtn,
  templateSuggestionFunc,
  suggestionFunc
) {
  // Configuración typeahead de input "Invitar usuario"
  $(searchInputTypeAheadSelector).typeahead(
    {
      hint: false,
      highlight: true,
      minLength: 3
    },
    {
      limit: 999,
      name: "states",
      source: function(query, cb, as) {
        axios.get("?search_text=" + query).then(function(response) {
          const values = Object.keys(response.data).map(function(e) {
            return response.data[e];
          });
          as(values); // Se hace la petición y con as() se colocan los datos a typeahead
        });
      },
      display: "search_text",
      templates: {
        empty:
          '<fieldset class="ag-form-invited_wrap\n' +
          "            ag-u-margin-both-40\n" +
          '            ag-js-postCard"' +
          "          >\n" +
          '            <figure class="ag-post-card\n' +
          '              ag-post-card_wrap"\n' +
          "            >\n" +
          '              <img class="ag-post-card__image"\n' +
          '                src="/static/biblored/img/message/not-found.svg"\n' +
          '                alt="No se encontraron personas sugeridas"\n' +
          "              >\n" +
          '              <figcaption class="ag-post-card__caption">\n' +
          "                Tu búsqueda no obtuvo ningún resultado. Intenta de nuevo con otro nombre, apellido o correo electrónico." +
          "              </figcaption>\n" +
          "            </figure>\n" +
          "          </fieldset>",
        suggestion: suggestionFunc
      }
    }
  );

  $(searchInputTypeAheadSelector).bind(
    "typeahead:beforeselect",
    (_e, suggestion) => {
      _e.preventDefault();
    }
  );

  // Funcionalidad eliminar usuario de lista para invitar
  document.addEventListener("click", function(e) {
    if (!e.target) {
      return;
    }
    const targetIsDeleteButton = e.target.classList.contains(
      "ag-js-userDeletetBtn"
    );
    const targetIsSelectButton = e.target.classList.contains(
      "ag-js-userSelectBtn"
    );
    if (targetIsDeleteButton || targetIsSelectButton) {
      const btn = e.target;
      const elementBox = btn.closest(".ag-js-inviteBox");
      let val = {};
      val["initials"] = elementBox
        .querySelector(".ag-list__content")
        .textContent.split(" ")
        .map(name => name.charAt(0))
        .join("");
      val["avatar"] =
        elementBox.querySelector("figure img") &&
        elementBox.querySelector("figure img").src;
      val["name"] = elementBox.querySelector(".ag-list__content").textContent;
      val["id"] = elementBox.querySelector(".ag-list__actions button").name;

      var nextState = "";

      if (targetIsDeleteButton) {
        let values = userListInput.value ? userListInput.value.split(",") : []; // Traemos el valor del input con la lista de usuarios  y lo convertimos a un array de todos los id seleccionados.

        // Se elimina el id (del usuario que se desea quitar de la lista de invitados) del input con la lista de usuarios
        values.splice(values.indexOf(btn.name), 1);
        userListInput.value = values;

        nextState = "toSelect";
      } else {
        const id = val["id"];
        let values = userListInput.value ? userListInput.value.split(",") : []; // Traemos el valor del input con la lista de usuarios  y lo convertimos a un array de todos los id seleccionados.

        values = values.map(x => x * 1); // Pasamos todos los valores del arreglo de string a enteros

        if (!values.includes(id)) {
          // Verifica que el usuario escogido no este ya en la lista de invitados
          // Agrega el nuevo usuario al input con la lista de usuarios
          values.push(id);
          userListInput.value = values.join(",");
        }

        nextState = "delete";
      }

      var parser = new DOMParser();
      var doc = parser.parseFromString(
        templateSuggestionFunc(val, nextState),
        "text/html"
      );
      const parentElement = elementBox.parentElement;
      parentElement.replaceChild(doc.body.firstElementChild, elementBox);
    }
  });

  function addWarningTooltip(requestForm, tooltipSearch) {
    tooltipSearch.removeAttribute("hidden");
    tooltipSearch.classList.add("ag-is-show");

    searchUserInput.classList.add("ag-is-warning");
  }

  function removeWarningTooltip(requestForm, tooltipSearch) {
    tooltipSearch.setAttribute("hidden", "hidden");
    tooltipSearch.classList.remove("ag-is-show");

    searchUserInput.classList.remove("ag-is-warning");
  }

  // Tooltip alerta buscador invitar
  const tooltipSearch = requestForm.querySelector(".ag-js-tip");
  const tooltipSearchSubmit = requestForm.querySelector(".ag-js-tip-submit");

  // Si al hacer submit no hay nada escrito aparece el tooltip de alerta.
  searchUserBtn.addEventListener("click", function(ev) {
    if (searchUserInput.value.length < 3) {
      ev.preventDefault();
      tooltipSearchSubmit &&
        removeWarningTooltip(requestForm, tooltipSearchSubmit);
      tooltipSearch && addWarningTooltip(requestForm, tooltipSearch);
    }
  });
  requestForm.addEventListener("submit", function(ev) {
    if (userListInput.value.length === 0) {
      ev.preventDefault();
      tooltipSearchSubmit &&
        addWarningTooltip(requestForm, tooltipSearchSubmit);
    }
  });

  // Al escribir algo en el search desaparece el tooltip de alerta.
  searchUserInput.addEventListener("input", function(ev) {
    if (searchUserInput.value.length > 2) {
      ev.preventDefault();
      tooltipSearch && removeWarningTooltip(requestForm, tooltipSearch);
      tooltipSearchSubmit &&
        removeWarningTooltip(requestForm, tooltipSearchSubmit);
    }
  });

  // Cierra sugerencias buscador usuarioes al dar click afuera
  document.addEventListener("mouseup", function(e) {
    if (searchUserInputWrapper && !searchUserInputWrapper.contains(e.target)) {
      const tooltipSearch = requestForm.querySelector(".ag-js-tip");
      const tooltipSearchSubmit = requestForm.querySelector(
        ".ag-js-tip-submit"
      );
      tooltipSearch && removeWarningTooltip(requestForm, tooltipSearch);
      tooltipSearchSubmit &&
        removeWarningTooltip(requestForm, tooltipSearchSubmit);
    }
  });
}
