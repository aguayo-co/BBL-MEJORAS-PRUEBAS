import { openModal } from "./components/c11_modal";

const btnMilestonePrev = document.querySelectorAll(
  ".js-pass-milestone-timeline-prev"
);

const btnMilestoneNext = document.querySelectorAll(
  ".js-pass-milestone-timeline-next"
);

btnMilestonePrev.forEach(btnPrev => {
  btnPrev.addEventListener("click", e => {
    let parentModal = btnPrev.closest(".ag-js-modal");
    let prevSibling = "";

    if (parentModal.previousElementSibling.classList.contains("ag-js-modal")) {
      prevSibling = parentModal.previousElementSibling;
    } else {
      prevSibling = parentModal.previousElementSibling.previousElementSibling;
    }

    parentModal.classList.remove("ag-is-modal_visible");
    document.body.classList.remove("ag-is-overflow");
    openModal(prevSibling);
  });
});

btnMilestoneNext.forEach(btnNext => {
  btnNext.addEventListener("click", e => {
    let parentModal = btnNext.closest(".ag-js-modal");
    let prevSibling = "";

    if (parentModal.nextElementSibling.classList.contains("ag-js-modal")) {
      prevSibling = parentModal.nextElementSibling;
    } else {
      prevSibling = parentModal.nextElementSibling.nextElementSibling;
    }

    parentModal.classList.remove("ag-is-modal_visible");
    document.body.classList.remove("ag-is-overflow");
    openModal(prevSibling);
  });
});
