const copyUrl = function() {
  const aux = document.createElement("input");
  const msgLinkCopy = document.getElementsByClassName("ag-js-copyUriMsg")[0];

  aux.setAttribute("value", window.location.href);
  document.body.appendChild(aux);
  aux.select();
  document.execCommand("copy");
  document.body.removeChild(aux);
  toggleMessage(msgLinkCopy);
};

const copyUriBtn = document.getElementsByClassName("ag-js-copyUri")[0];
const copyUriBtnsMilestone = document.querySelectorAll(
  ".ag-js-copyUriTimeline"
);

function updateURLParameter(url, param, paramVal) {
  var newAdditionalURL = "";
  var tempArray = url.split("?");
  var baseURL = tempArray[0];
  var additionalURL = tempArray[1];
  var temp = "";
  if (additionalURL) {
    tempArray = additionalURL.split("&");
    for (var i = 0; i < tempArray.length; i++) {
      if (tempArray[i].split("=")[0] != param) {
        newAdditionalURL += temp + tempArray[i];
        temp = "&";
      }
    }
  }

  var rows_txt = temp + "" + param + "=" + paramVal;
  return baseURL + "?" + newAdditionalURL + rows_txt;
}

function copyUrlOfTimelineMilestone() {
  copyUriBtnsMilestone.forEach(currentBtn => {
    currentBtn.addEventListener("click", () => {
      const id_milestone = currentBtn
        .closest(".ag-js-modal-milestone")
        .getAttribute("id");
      const aux = document.createElement("input");
      const msgLinkCopy = currentBtn.querySelector(".ag-js-copyUriMsg");

      const urlToShare = updateURLParameter(
        window.location.href,
        "milestone",
        id_milestone
      );

      aux.setAttribute("value", urlToShare);
      document.body.appendChild(aux);
      aux.select();
      document.execCommand("copy");
      document.body.removeChild(aux);
      toggleMessage(msgLinkCopy);
    });
  });
}

function copyUrlInAnotherPages() {
  const btnCopyUrl = document.querySelectorAll(".ag-js-copyUrlAnotherPage");
  const aux = document.createElement("input");

  btnCopyUrl.forEach(btnCurrent => {
    const msgLinkCopy = btnCurrent.querySelector(".ag-js-copyUriMsg");

    btnCurrent.addEventListener("click", () => {
      const linkForCopy = btnCurrent.closest(".ag-js-modal")
        .previousElementSibling;

      aux.setAttribute("value", createHrefForLink(linkForCopy));

      btnCurrent.parentElement.appendChild(aux);
      aux.select();
      document.execCommand("copy");
      btnCurrent.parentElement.removeChild(aux);

      toggleMessage(msgLinkCopy);
    });
  });
}

function toggleMessage(msgLinkCopy) {
  msgLinkCopy.classList.add("ag-is-ico-list_show");
  setTimeout(() => {
    msgLinkCopy.classList.remove("ag-is-ico-list_show");
  }, 2000);
}

function createHrefForLink(linkForCopy) {
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  let link = linkForCopy.querySelector("a[href]");
  if (link == null) {
    return linkForCopy.baseURI;
  }
  return protocol + "//" + hostname + link.getAttribute("href");
}

copyUriBtn && copyUriBtn.addEventListener("click", copyUrl);
copyUrlInAnotherPages();
copyUrlOfTimelineMilestone();
