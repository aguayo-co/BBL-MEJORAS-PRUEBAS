function getMaxCaracters() {
  return 426;
}

function getContainerText() {
  return document.querySelectorAll(".ag-js-counterTextSlideUp");
}

function closeAllQuote() {
  document
    .querySelectorAll("span[is-open='true']")
    .forEach(e => showLessContent(e));
}

function showLessContent(linkElement) {
  const parentBoxQuote = linkElement
    .closest(".ag-js-quoteWrap")
    .closest(".ag-js-quote");
  parentBoxQuote.classList.remove("ag-is-quote__show-text");
  linkElement.setAttribute("is-open", "");
  linkElement.innerHTML = "// Ver más";
}

function showMoreContent(linkElement) {
  closeAllQuote();
  const parentBoxQuote = linkElement
    .closest(".ag-js-quoteWrap")
    .closest(".ag-js-quote");
  parentBoxQuote.classList.add("ag-is-quote__show-text");
  linkElement.setAttribute("is-open", true);
  linkElement.innerHTML = "// Ver menos";
}

/* This function counter the characters in box
and if check the limit characters add the class in button */
function getCounterQuoteText(quoteContainer) {
  const containerText = getContainerText(quoteContainer);

  containerText.forEach(boxElement => {
    const contentElement = boxElement.innerHTML;
    const numberCharacters = contentElement.length;

    // Is counter the limit characters for appear the button
    if (numberCharacters > getMaxCaracters()) {
      const parentBoxQuote = boxElement.closest(".ag-js-quote");
      const childButtonBoxQuote = parentBoxQuote.querySelector(
        ".ag-js-btnCounterText"
      );

      // You can see the button with the class show
      childButtonBoxQuote.classList.add("ag-is-quote__show-btn");
    }
  });
}

function actionBtnOpen() {
  const getButtonHasClass = document.querySelectorAll(
    ".ag-js-btnCounterText.ag-is-quote__show-btn"
  );

  getButtonHasClass.forEach(actionButton => {
    actionButton.addEventListener("click", function() {
      const linkElement = actionButton.querySelector(".ag-js-linkChangeText");
      const isOpen = linkElement.getAttribute("is-open");

      if (isOpen) {
        showLessContent(linkElement);
      } else {
        showMoreContent(linkElement);
      }
    });
  });
}

export default function initCounterQuoteComponent() {
  getCounterQuoteText();
  actionBtnOpen();
}
