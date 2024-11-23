export function addMessage(status, message) {
  const messageTemplate = document.querySelector("#ag-js-message_template");
  if (messageTemplate) {
    const messageElement = messageTemplate.content.cloneNode(true);
    const messageElementUl = messageElement.querySelector(
      "div.ag-js-o-messages > ul.ag-js-o-messagesUl"
    );
    if (status >= 200 && status < 300) {
      messageElementUl.classList.add("ag-o-messages__success");
    } else {
      messageElementUl.classList.add("ag-o-messages__error");
    }
    messageElementUl.querySelector(
      "li.js-messagesItem > span.ag-js-o-messagesItemAlert > span.ag-js-o-messagesItemlead"
    ).innerHTML = message;
    document.body.appendChild(messageElement);
  }
}
