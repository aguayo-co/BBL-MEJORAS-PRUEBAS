import { getCookie } from "../utils/cookies";
import { addMessage } from "../utils/messages";
import { changeImagesButton } from "../utils/changeImagesFavoriteButton";
import setAlerts from "../components/alert";

const CSRF_TOKEN = getCookie("csrftoken");

function collectionFavoritesApiRequest(btn, RESTMethod, body) {
  var responseStatus = 200;
  var responseMessage = "";
  fetch(`/api/collections/${btn.dataset.collection}/favorites-group/`, {
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
      btn.dataset.inFavorites = Number(!Number(btn.dataset.inFavorites));
      const numberData = btn.dataset.inFavorites;
      if (btn.dataset.inFavorites == 1) {
        changeImagesButton(btn, numberData);
      } else changeImagesButton(btn, numberData);
    })
    .catch(err => {
      responseStatus = 500;
      responseMessage = err;
      addMessage(responseStatus, responseMessage);
      setAlerts();
    });
}

const addToFavoritesButtons = document.querySelectorAll(
  ".ag-js-CollectionsGroupAddToFavorites"
);

addToFavoritesButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    const formData = new FormData();
    formData.append("model_name", btn.dataset.modelName);
    const inFavorites = Number(btn.dataset.inFavorites);
    const RESTMethod = inFavorites ? "DELETE" : "POST";
    const data = new URLSearchParams(formData);
    collectionFavoritesApiRequest(btn, RESTMethod, data);
  });
});
