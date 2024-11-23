import {
  addDeleteListItemEventsListeners,
  addDeleteDetailPageObjectEventsListeners
} from "../utils/deleteModals";

addDeleteListItemEventsListeners(
  "ag-js-deleteCollectionFromCollectionsGroupPk",
  "ag-js-deleteCollectionFromCollectionsGroup"
);
addDeleteDetailPageObjectEventsListeners("ag-js-deleteCollectionsGroupBtn");
