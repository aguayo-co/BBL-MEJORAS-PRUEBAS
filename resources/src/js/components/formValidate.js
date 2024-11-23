const validate = {
  messages: {
    // Mensajes de validación
    "document-required": "Escribe tu número de documento de identidad ",
    "password-required": "Escribe tu contraseña",
    "terms-required": "Debes aceptar los términos y condiciones",
    "biography-required": "Escribe tu biografía",
    "select-country": "Selecciona un país.",
    "collection-required":
      "Debes seleccionar al menos una colección o colección colaborativa.",
    "reviews-title-required": "Ingresa un título para tu reseña",
    "reviews-required": "Ingresa una reseña",
    "review-text-min-length":
      "Tu reseña debe tener un mínimo de 100 caracteres",
    "rating-required":
      "Califica el contenido con 1 a 5 aplausos para guardar tu reseña.",
    "title-required": "Debes escribir el nombre de tu colección",
    "description-required":
      "Debes escribir una descripción para crear tu colección",
    "cover-photo-required": "Debes seleccionar una foto de portada."
  },
  rules: {
    // Reglas de validación
    "document-required": function(input) {
      const val = input.value;
      return val.length > 0;
    },
    "password-required": function(input) {
      const val = input.value;
      return val.length > 0;
    },
    "terms-required": function(input) {
      return input.checked;
    },
    "biography-required": function(input) {
      const val = input.value;
      return val.length > 0;
    },
    "select-country": function(input) {
      const val = input.value;
      return val.length > 0;
    },
    "collection-required": function(input) {
      const name = input.name;
      return (
        document.querySelectorAll('input[name="' + name + '"]:checked').length >
          0 ||
        document.querySelectorAll(
          'input[name="collaborative_collections"]:checked'
        ).length > 0
      );
    },
    "reviews-required": function(input) {
      const val = input.value;
      return val.length > 0;
    },
    "reviews-title-required": function(input) {
      const val = input.value;
      return val.length > 0;
    },
    "review-text-min-length": function(input) {
      const val = input.value;
      return val.length < 100;
    },
    "rating-required": function(input) {
      const container = input.closest(".ag-js-formInput");

      return container.querySelectorAll('[name="rating"]:checked').length > 0;
    },
    "title-required": function(input) {
      const val = input.value;
      return val.length > 0;
    },
    "description-required": function(input) {
      const val = input.value;
      return val.length > 0;
    },
    "cover-photo-required": function(input) {
      const val = input.value;
      return val.length > 0;
    }
  },
  valid(el) {
    // Valida un input, debe tener name y data-validate que exista en rules, retorna true si el input es valido de lo contrario retorna false
    let validations = el
        .getAttribute("data-validate")
        .replace(/\s/g, "")
        .split("|"),
      input = el.querySelector("input, select, textarea"),
      name = input.name,
      messageElement = input.form.querySelector(
        `.ag-js-msgError[data-for='${name}']`
      );

    for (let i = 0; i < validations.length; i++) {
      if (!this.rules[validations[i]]) {
        return undefined;
      }
      if (this.rules[validations[i]](input)) {
        if (messageElement) {
          el.classList.remove("ag-is-error", "i-close");
          messageElement
            ? (messageElement.innerText = "")
            : console.error(
                `No existe el elemento para el mensaje de error .ag-js-msgError[data-for='${name}']`
              );
          messageElement.setAttribute("hidden", "");
          messageElement.removeAttribute("role");
        }
        return true;
      } else {
        if (messageElement) {
          el.classList.add("ag-is-error", "i-close");
          messageElement.innerText = this.messages[validations[i]];
          messageElement.removeAttribute("hidden");
          messageElement.setAttribute("role", "alert");
        }
        return false;
      }
    }
  },
  validForm(el) {
    // Al darle click a un botón, valida los inputs que estén dentro de su mismo fieldset padre. Retorna true si todos los inputs son validos de lo contrario retorna false
    let inputs = Array.from(
        el.querySelectorAll(".ag-js-formInput[data-validate]")
      ),
      isValid = true;

    for (var i = 0; i < inputs.length; i++) {
      if (!this.valid(inputs[i])) {
        isValid = false;
      }
    }
    return isValid;
  },
  clear(form) {
    const msgError = Array.from(form.getElementsByClassName("ag-js-msgError"));
    msgError.forEach(msg => {
      const agName = msg.getAttribute("data-for"),
        input = document.querySelector(`[name='${agName}']`),
        formField = input.closest(".ag-js-form__field");
      input && input.classList.remove("ag-is-error", "i-close");
      formField && formField.classList.remove("ag-is-error");
      if (msg) {
        msg.innerText = "";
        msg.setAttribute("hidden", "");
      }
    });
  }
};

if (document.getElementsByClassName("ag-js-validate")[0]) {
  const formToValidate = Array.from(
    document.getElementsByClassName("ag-js-validate")
  );
  formToValidate.forEach(x => {
    x.addEventListener("submit", function(e) {
      e.preventDefault();
      // Se ejecuta la validación personalizadas y si es valido se hace submit.
      validate.validForm(this) && this.submit();
    });
    // Validaciones nativas HTML5
    x.addEventListener(
      "invalid",
      function(e) {
        // Hacemos preventDefault() para no mostrar los popup o los estilos de los mensajes por defecto de los navegadores.
        e.preventDefault();

        const input = e.target, // Input invalido.
          errorMsg = input.validationMessage, // Mensaje de error por defecto de HTML5 del input invalido.
          messageElement = document.querySelector(
            `.ag-js-msgError[data-for='${input.name}']`
          ),
          formField = input.closest(".ag-js-form__field");

        // Limpiamos los mensajes de error si existe alguno
        validate.clear(this);

        // Colocamos los mensajes de validación del navegador con estilos propios de la biblioteca.
        input.classList.add("ag-is-error", "i-close");
        if (messageElement) {
          messageElement.innerText = errorMsg;
          messageElement.removeAttribute("hidden");
        } else {
          console.error(
            `No existe el elemento para el mensaje de error .ag-js-msgError[data-for='${input.name}']`
          );
        }
        formField && formField.classList.add("ag-is-error");

        // Se ejecuta la validación personalizadas y si es valido se hace submit.
        validate.validForm(x);
      },
      true
    );
  });
}

/**
 * Lógica contador de caracteres input
 * En el html la estructura debe estar asi:
 * Ejemplo:
 <div class="ag-form__field ag-js-form__field">
 <label class="ag-form__label">Bio</label>
 <div class="ag-form__input ag-js-formTextarea">
 <textarea name="biography" cols="40" rows="10" maxlength="800" required="" id="id_biography"></textarea>
 <span class="ag-form__helper ag-js-inputCharsCounter" data-for="biography">800/800</span>
 </div>
 </div>

 * Clases y atributos importantes para el correcto funcionamiento:
 - .ag-js-form__field : Clase del contenedor del input con su label y el contador.

 - .ag-js-inputCharsCounter : Clase para identificar los elementos que son contadores y a los cuales se les aplicara la lógica.
 - [data-for] : Atributo que vincula el elemento contador (el que tiene la clase .ag-js-inputCharsCounter) con el input, en este atributo debe ir en 'name' del input.

 - [maxlength] : Atributo que indica cuanto es el máximo de caracteres que acepta el input, debe ir en el input.
 - [name] : nombre del input, el cual se usa para vincularlo con el contador, en 'name' se debe colocar en la propiedad [data-for] del contador.
 */
// Seleccionamos todos los contadores que existen en la pagina.
const inputCharsCounter = Array.from(
  document.getElementsByClassName("ag-js-inputCharsCounter")
);
// Agregamos la lógica del contador de caracteres a todos los contadores que encontramos.
inputCharsCounter.forEach(counter => {
  // Obtenemos los elementos y datos necesarios.
  const agFor = counter.getAttribute("data-for"),
    container = counter.closest(".ag-js-form__field"),
    input = container.querySelector(`[name='${agFor}']`),
    maxLength = input.getAttribute("maxlength");
  // Al input asociado al contador le agregamos el evento 'keyup' para detectar cuando se este escribiendo en el input y asi ir actualizando el contador.
  input.addEventListener("input", function() {
    // Saltos de línea se cuentan como dos caracteres.
    const value = input.value.replace(/(\r\n|\n|\r)/g, "  ");
    const valueLength = value.length;
    // Colocamos el texto en el contador, ejemplo: '123/800'
    counter.innerText = `${valueLength}/${maxLength}`;
    // Si la cantidad de caracteres es igual a la cantidad maxima de caracteres en el input [maxlength] se agrega la clase de error '.ag-is-error', si no la elimina si la tiene.
    if (valueLength > maxLength) {
      container.classList.add("ag-is-error");
    } else if (container.classList.contains("ag-is-error")) {
      container.classList.remove("ag-is-error");
    }
  });
  input.dispatchEvent(new Event("input"));
});
