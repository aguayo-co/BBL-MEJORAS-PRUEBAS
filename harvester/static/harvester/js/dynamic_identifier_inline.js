$(document).ready(function() {
  let $ = django.jQuery;
  let base_url = JSON.parse(
    document.getElementById("dynamic_identifier_url").textContent
  );

  // Determine Fields
  let id = "id_dynamicidentifierconfig_set-0-field";

  // Test Button action
  $("input.dynamic_identifier_test_button").each(function(
    index,
    button,
    array
  ) {
    $(button).click(function() {
      let data_source = document.URL.replace(/[A-Za-z$-/:?]/g, "");
      let result_table = $("#dynamic_identifier_result_table");
      let total_forms = $("#id_dynamicidentifierconfig_set-TOTAL_FORMS").val();
      let fields = [];
      let expressions = [];
      let is_valid = false;

      //TODO VALIDAR CAMPOS AQUI
      for (let i = 0; i < total_forms; i++) {
        let field = $(`#id_dynamicidentifierconfig_set-${i}-field`);
        let expression = $(
          `#id_dynamicidentifierconfig_set-${i}-capture_expression`
        );
        fields[i] = field.val();
        expressions[i] = expression.val();
        is_valid = validate_fields(field, expression);
      }
      if (is_valid && fields[0] && expressions[0]) {
        result_table.find(".result_row").remove();
        result_table.append(
          `<tr class='result_row'><td colspan="2">Cargando...</td></tr>`
        );

        $.get(base_url.replace("0", data_source), {
          "fields[]": fields,
          "expressions[]": expressions
        })
          .done(function(data) {
            $("#result_header_dynamic_identifier").show();
            result_table.find(".result_row").remove();
            if (!data_source) {
              result_table.append(
                `<tr class='result_row'><td colspan="2">Debe cosechar esta fuente antes de probar el Identificador Dinámico</td></tr>`
              );
            } else {
              data.forEach(function(dynamic_identifier) {
                result_table.append(
                  `<tr class='result_row'><td>${dynamic_identifier[0]}</td><td>${dynamic_identifier[1]}</td></tr>`
                );
              });
            }
          })
          .fail(function(error) {
            result_table.find(".result_row").remove();
            result_table.append(
              `<tr class='result_row'><td>Error: ${error.status}</td><td>${error.statusText}</td></tr>`
            );
          });
      }
    });
  });
});
function validate_fields(field, expression) {
  let field_val = field.val();
  let expression_val = expression.val();
  let invalid_fields = [];
  let valid_fields = [field, expression];

  if (!field_val) {
    invalid_fields.push(field);
    valid_fields.splice(valid_fields.indexOf(field), 1);
  }
  if (!expression_val) {
    invalid_fields.push(expression);
    valid_fields.splice(valid_fields.indexOf(expression), 1);
  }

  valid_fields.forEach(input => {
    input.closest(".form-row").removeClass("errors");
    input
      .closest(".form-row")
      .find("ul")
      .remove();
  });

  // Empty pair is valid
  if ((!field_val && !expression_val) || (field_val && expression_val)) {
    return true;
  }

  invalid_fields.forEach(input => {
    input.closest(".form-row").removeClass("errors");
    input
      .closest(".form-row")
      .find("ul")
      .remove();
    input.closest(".form-row").addClass("errors");
    input
      .parent()
      .before('<ul class="errorlist"><li>Este campo es obligatorio.</li></ul>');
  });

  return false;
}
