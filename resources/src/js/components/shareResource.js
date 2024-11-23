import {
  getUsersListValues,
  templateSuggestion,
  initUserSearchSuggestions
} from "../utils/searchUserTypeAheadWithListForm";

const searchInputTypeAheadSelector = "#invite-users";
const inputUsers = document.querySelector('input[name="users"]');
const requestForm = document.getElementById("share-resource-form");
const searchUserInput = requestForm.querySelector("#invite-users");
const searchUserInputWrapper = requestForm.querySelector(
  ".ag-js-searchUserInput"
);
const searchUserBtn = requestForm.querySelector(".ag-js-searchUserBtn");

const suggestion = function(user) {
  const values = getUsersListValues(inputUsers);
  const id = user.id;

  if (user.shared_date) {
    const yesterdayDate = new Date();
    yesterdayDate.setDate(yesterdayDate.getDate() - 1);
    const yesterdayTime = yesterdayDate.getTime();
    const sharedDate = Date.parse(user.shared_date);
    if (sharedDate > yesterdayTime) {
      return templateSuggestion(user, "shared");
    }
  }
  // Renderiza lista de sugerencias en el buscador de invitar usuario
  if (values.includes(id)) {
    return templateSuggestion(user, "delete"); // Si el id de la sugerencia existe en el arreglo values (o sea ya esta seleccionado) se enviá el template con estado 'select'.
  } else {
    return templateSuggestion(user, "toSelect"); // Si el id de la sugerencia no existe en el arreglo values (o sea no esta seleccionado) se enviá el template con estado 'toSelect'.
  }
};

initUserSearchSuggestions(
  searchInputTypeAheadSelector,
  inputUsers,
  requestForm,
  searchUserInputWrapper,
  searchUserInput,
  searchUserBtn,
  templateSuggestion,
  suggestion
);
