import { getCookie } from "../utils/cookies";
import { addMessage } from "../utils/messages";
import setAlerts from "../components/alert";

const CSRF_TOKEN = getCookie("csrftoken");

function ignoreSharedResourceApiRequest(btn) {
  var responseStatus = 200;
  var responseMessage = "";
  fetch(`/api/shared-resources/${btn.dataset.notificationId}/ignore/`, {
    method: "POST",
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

const ignoreSharedResourceButtons = document.querySelectorAll(
  ".ag-js-ignore_shared_resource"
);

ignoreSharedResourceButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    ignoreSharedResourceApiRequest(btn);
    btn.disabled = true;
    location.reload();
  });
});
