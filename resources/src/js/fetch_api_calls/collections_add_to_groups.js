import { getCookie } from "../utils/cookies";
import { addMessage } from "../utils/messages";
import setAlerts from "../components/alert";

const CSRF_TOKEN = getCookie("csrftoken");

function collectionAddToGroupsApiRequest(btn, RESTMethod, body) {
  var responseStatus = 200;
  var responseMessage = "";
  fetch(`/api/collections/${btn.dataset.collection}/add-to-groups/`, {
    method: RESTMethod,
    body: body,
    headers: { "X-CSRFToken": CSRF_TOKEN }
  })
    .then(response => {
      responseStatus = response.status;
      if (responseStatus >= 200 && responseStatus < 300) {
        return response.json();
      } else {
        return Promise.reject("Error, intentalo de nuevo;");
      }
    })
    .then(json => {
      responseMessage = json.message;
      addMessage(responseStatus, responseMessage);
      setAlerts();
    })
    .catch(err => {
      responseStatus = 500;
      responseMessage = err;
      addMessage(responseStatus, responseMessage);
      setAlerts();
    });
}

const addToGroupsButtons = document.querySelectorAll(
  ".ag-js-collectionAddToGroupsFormSubmit"
);

addToGroupsButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    const form = btn.closest("form");
    const data = new URLSearchParams(new FormData(form));
    collectionAddToGroupsApiRequest(btn, "POST", data);
  });
});
