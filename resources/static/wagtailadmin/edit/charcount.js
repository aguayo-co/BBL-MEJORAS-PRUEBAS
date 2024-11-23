$(function() {
  // Normal text fields
  let text_fields = $($("form").find(".field.char_field"));
  text_fields.each(function() {
    // Count Chars
    var helpBox = $(this).find(".help");
    if (helpBox.html()) {
      helpBox.addClass("charcount");
    } else {
      $(this)
        .find(".field-content")
        .append("<p class='help charcount'></p>");
      helpBox = $(this).find(".charcount");
      helpBox.hide();
    }
    var whiteSpace = /\s\s+/gm;
    var charCountElemText = helpBox.text();
    var maxChars = $(this)
      .find("input")
      .attr("maxlength");

    // Draftail
    $($(this).find(".public-DraftEditor-content")).bind("input", function() {
      $(this)
        .closest(".field-content")
        .find("input")
        .trigger("propertychange");
    });

    $($(this).find("input, textarea")).bind(
      "input propertychange change",
      function() {
        var text = this.value;
        try {
          var json_value = JSON.parse(this.value);
          if (typeof json_value !== "string" && json_value.blocks[0].text) {
            text = json_value.blocks[0].text;
          }
        } catch (e) {}

        if (this.maxLength > 1) {
          maxChars = this.maxLength;
        }
        if (maxChars === undefined) {
          return;
        }
        var textNoWhitespace = text
          .replace(whiteSpace, " ")
          .replace("\n", "")
          .replace("\r\n", "")
          .replace("\r\n", "");
        var textCharCount = textNoWhitespace.length;
        if (charCountElemText.length > 1) {
          helpBox.css({ opacity: 1 });
          var helpBoxContent =
            charCountElemText +
            "<p class='count'>" +
            textCharCount +
            " / " +
            maxChars +
            " caracteres</p>";
          helpBox.html(helpBoxContent);
        } else {
          helpBox.show();
          helpBox.html(
            "<p class='count'>" +
              textCharCount +
              " / " +
              maxChars +
              " caracteres </p>"
          );
        }

        if (textCharCount >= parseInt(maxChars)) {
          $(helpBox.find(".count")).css({ color: "red" });
        } else if (textCharCount + 10 > maxChars) {
          $(helpBox.find(".count")).css({ color: "orange" });
        }
      }
    );
  });
});
