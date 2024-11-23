$(document).ready(function() {
  let $ = django.jQuery;
  // Determine Fields
  // Valid for use two or more capture_expression_widget in the same page
  let fields = $.uniqueSort(
    $(".capture_expression_widget").map(function() {
      let pattern = new RegExp(".+?(?=_0)");
      return pattern.exec(this.id);
    })
  );

  fields.each(function() {
    const field = this;
    let field_zero = $(`#${field}_0`);
    let tr_field_one = $(`#tr_for_${field}_1`);
    let field_one = $(`#${field}_1`);
    //_0 Method
    field_zero.on("change", function() {
        const capture_action = $(this).val();
        let show_custom_expression_field = false;
        field_one.prop("disabled", true);
        tr_field_one.hide();
        switch (capture_action) {
          case "custom":
            //Hide field _2 (Url)
            tr_field_one.show();
            field_one.prop("disabled", false);
            show_custom_expression_field = true;
            break;
        }

        //Show url field
        if (show_custom_expression_field) {
          tr_field_one.show();
          field_one.prop("disabled", false);
        }
    });

    // Trigger all events on load
    field_zero.change();
    field_zero.find("select").each(function() {
      $(this).change();
    });
    field_one.change();
  });
});
