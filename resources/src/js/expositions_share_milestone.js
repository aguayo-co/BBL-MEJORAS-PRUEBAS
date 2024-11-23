import { openModal } from "./components/c11_modal";

function getParameterByName(name) {
  name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
  var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
    results = regex.exec(location.search);
  return results === null
    ? ""
    : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function shareMilestoneTimeline() {
  const modalsMilestone = document.querySelectorAll(".ag-js-modal-milestone");

  modalsMilestone.forEach(modalSelected => {
    const idMilestone = modalSelected.getAttribute("id");
    const paramUrl = getParameterByName("milestone");

    if (paramUrl == idMilestone) {
      openModal(modalSelected);
    }
  });
}

shareMilestoneTimeline();
