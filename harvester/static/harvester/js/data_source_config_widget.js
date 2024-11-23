$(document).ready(function() {
  let $ = django.jQuery;
  // Determine Fields
  // Valid for use two or more data_source_config_widget in the same page
  let fields = $.uniqueSort(
    $(".data_source_config_widget").map(function() {
      let pattern = new RegExp(".+?(?=_0)");
      return pattern.exec(this.id);
    })
  );

  fields.each(function() {
    const field = this;
    let field_zero = $(`#${field}_0`);
    let field_one = $(`#${field}_1`);
    let tr_field_two = $(`#tr_for_${field}_2`);
    let field_two = $(`#${field}_2`);
    //_0 Method
    field_zero.find("input").each(function() {
      $(this).on("change", function() {
        const method = $(this).val();
        let show_url_field = false;
        switch (method) {
          case "upload":
            //Hide field _2 (Url)
            tr_field_two.hide();
            field_two.prop("disabled", true);
            //Can't select DUBLIN_CORE
            cant_select_dublin_core(field);
            break;
          case "url":
            //Can't select DUBLIN_CORE
            cant_select_dublin_core(field);
            show_url_field = true;
            break;
          case "api":
            //Only can select DUBLIN_CORE
            only_can_select_dublin_core(field);
            show_url_field = true;
            break;
        }

        //Show url field
        if (show_url_field) {
          tr_field_two.show();
          field_two.prop("disabled", false);
        }
      });
    });

    //_1 format
    field_one.on("change", function() {
      const format = $(this).val();
      const fields_numbers = ["3", "4"];
      fields_numbers.forEach(function(field_number) {
        if (format === "csv") {
          $(`#tr_for_${field}_${field_number}`).show();
          $(`#${field}_${field_number}`).prop("disabled", false);
        } else {
          $(`#tr_for_${field}_${field_number}`).hide();
          $(`#${field}_${field_number}`).prop("disabled", true);
        }
      });
    });

    // Trigger all events on load
    field_zero.change();
    field_zero.find("input:checked").each(function() {
      $(this).change();
    });
    field_one.change();
  });

  /**
   * Disables the dublin_core option for this field
   * @param  {String} field a base field name
   */
  function cant_select_dublin_core(field) {
    $(`#${field}_1`)
      .find("option")
      .each(function() {
        $(this).prop("disabled", false);
        if ($(this).val() === "oai_dc") {
          $(this).prop("disabled", true);
        }
      });
    select_valid_option(field);
  }

  /**
   * Enables the dublin_core option and the empty choice for this field
   * @param  {String} field a base field name
   */
  function only_can_select_dublin_core(field) {
    $(`#${field}_1`)
      .find("option")
      .each(function() {
        $(this).prop("disabled", true);
        if ($(this).val() === "oai_dc" || $(this).val() === "") {
          $(this).prop("disabled", false);
        }
      });
    select_valid_option(field);
  }

  /**
   * Given a field check if the selected option is a valid choice based in its visibility
   * @param  {String} field a base field name
   */
  function select_valid_option(field) {
    let field_one = $(`#${field}_1`);
    field_one.find("option:selected").each(function() {
      if ($(this).is(":disabled")) {
        $(`#${field}_1`).val("");
      }
    });
    field_one.change();
  }
});
