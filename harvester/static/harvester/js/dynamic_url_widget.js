$(document).ready(function() {
  // Capitalize
  String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
  };

  let $ = django.jQuery;
  let base_url = JSON.parse(document.getElementById("regex_url").textContent);
  // Determine Fields
  let fields = $.uniqueSort(
    $(".dynamic_url_widget").map(function() {
      let pattern = new RegExp(".+?(?=_0)");
      return pattern.exec(this.id);
    })
  );

  //hide initial
  fields.each(function(index, field, array) {
    let field_zero = $(`#${field}_0`);
    let subwidget_one = $(`#subwidget_${field}_1`);
    let subwidget_two = $(`#subwidget_${field}_2`);
    let table = $(`#table_for_${field}`);
    field_zero.change(function() {
      if (!$(this).val()) {
        subwidget_one.hide();
        subwidget_one.find("input").prop("disabled", true);
        subwidget_two.hide();
        subwidget_two.find("input").prop("disabled", true);
        $(`#button_row_${field}`).hide();
        $(`#result_header_${field}`).hide();
        table.find(".result_row").hide();
        table.find(".help").hide();
      } else {
        $(`#result_header_${field}`).hide();
        subwidget_one.show();
        subwidget_one.find("input").prop("disabled", false);
        subwidget_two.show();
        subwidget_two.find("input").prop("disabled", false);
        table.find(".help").show();
        $(`#button_row_${field}`).show();
      }
    });
    field_zero.change();
  });

  // Button action
  $("input.dynamic_url_widget_button").each(function(index, button, array) {
    $(button).click(function() {
      let params = [];
      fields.each(function(index, field, array) {
        params[index] = {
          field: $(`#${field}_0`).val(),
          capture_expression: $(`#${field}_1`).val(),
          replace_expression: $(`#${field}_2`).val(),
          data_source: document.URL.replace(/[A-Za-z$-/:?]/g, "")
        };
      });
      $.get(
        base_url.replace("0", params[index].data_source),
        params[index]
      ).done(function(data) {
        $(`#result_header_${fields[index]}`).show();
        $(`#field_header_${fields[index]}`).text(
          `${params[index].field}`.capitalize()
        );
        $(`#table_for_${fields[index]}`)
          .find(".result_row")
          .remove();
        data.forEach(function(testUrl) {
          $(`#table_for_${fields[index]}`).append(
            `<tr class='result_row'><td>${testUrl[0]}</td><td><a href="${testUrl[1]}" target="_blank">${testUrl[1]}</a></td></tr>`
          );
        });
      });
    });
  });
});
