import {
  getUsersListValues,
  templateSuggestion,
  initUserSearchSuggestions
} from "../utils/searchUserTypeAheadWithListForm";

const searchInputTypeAheadSelector = "#invite-collaborators";
const inputCollaborators = document.querySelector(
  'input[name="collaborators"]'
);
const requestForm = document.getElementById("invite-form");
const searchCollaboratorInput = requestForm.querySelector(
  "#invite-collaborators"
);
const searchCollaboratorInputWrapper = requestForm.querySelector(
  ".ag-js-searchCollaboratorInput"
);
const searchCollaboratorBtn = requestForm.querySelector(
  ".ag-js-searchCollaboratorBtn"
);

const suggestion = function(user) {
  const values = getUsersListValues(inputCollaborators);
  const id = user.id;
  // Renderiza lista de sugerencias en el buscador de invitar usuario\

  if (values.includes(id)) {
    return templateSuggestion(user, "delete"); // Si el id de la sugerencia existe en el arreglo values (o sea ya esta seleccionado) se enviá el template con estado 'select'.
  } else {
    return templateSuggestion(user, "toSelect"); // Si el id de la sugerencia no existe en el arreglo values (o sea no esta seleccionado) se enviá el template con estado 'toSelect'.
  }
};

initUserSearchSuggestions(
  searchInputTypeAheadSelector,
  inputCollaborators,
  requestForm,
  searchCollaboratorInputWrapper,
  searchCollaboratorInput,
  searchCollaboratorBtn,
  templateSuggestion,
  suggestion
);
