import {
  addDeleteListItemEventsListeners,
  addDeleteDetailPageObjectEventsListeners
} from "../utils/deleteModals";

addDeleteListItemEventsListeners(
  "ag-js-deleteResourcePk",
  "ag-js-deleteResource"
);
addDeleteDetailPageObjectEventsListeners("ag-js-deleteCollectionBtn");
