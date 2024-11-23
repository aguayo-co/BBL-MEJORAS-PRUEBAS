class Tabs {
  constructor(classButtonActive, classContentHide) {
    this.actionTabs = Array.from(
      document.querySelectorAll("[data-button-tabs]")
    );
    this.contentTabs = Array.from(
      document.querySelectorAll("[data-content-tabs")
    );
    this.classButtonActive = classButtonActive;
    this.classContentHide = classContentHide;
    this.init();
  }

  init() {
    this.hideContentTabs();
    this.showHoverInSelectImage();
    this.showPreviewImageChoice();
  }

  hideContentTabs() {
    this.actionTabs.map(e => {
      e.addEventListener("click", () => {
        this.contentTabs.forEach(contentCurrent => {
          if (
            e.getAttribute("data-button-tabs") ==
            contentCurrent.getAttribute("data-content-tabs")
          ) {
            e.classList.add(this.classButtonActive);
            contentCurrent.classList.remove(this.classContentHide);
            this.actionTabs.forEach(siblingButtons => {
              if (
                siblingButtons.getAttribute("data-button-tabs") !=
                contentCurrent.getAttribute("data-content-tabs")
              ) {
                siblingButtons.classList.remove(this.classButtonActive);
              }
            });
          } else {
            contentCurrent.classList.add(this.classContentHide);
          }
        });
      });
    });
  }

  showHoverInSelectImage() {
    const radioButton = Array.from(
      document.querySelectorAll("[name='default_cover_image'")
    );
    const selectImage = Array.from(
      document.querySelectorAll(".ag-js-choice-image")
    );

    radioButton.map(e => {
      e.addEventListener("click", () => {
        selectImage.forEach(image => {
          if (image.classList.contains(e.getAttribute("id"))) {
            const containerFinalImage = document.querySelector(
              ".ag-js-img-croped"
            );
            const containerImgShow = document.querySelector(
              ".ag-js-fileUpload"
            );
            const img = document.createElement("img");
            var imageChoice = image.querySelector("img");

            image.classList.add("ag-is-image-selected");
            image.classList.add("ag-is-choice-image-check");

            if (containerFinalImage.children.length > 0) {
              containerFinalImage.removeChild(
                document.querySelector(".ag-js-croped-img")
              );
            }

            document.querySelector(
              ".ag-js-imageUploadedName"
            ).innerHTML = imageChoice.getAttribute("alt");

            containerImgShow.style.display = "flex";
            //Set data for show crop image in the form
            img.setAttribute("src", imageChoice.getAttribute("src"));
            img.classList.add("ag-is-preview-choice-img");
            img.classList.add("ag-js-croped-img");
            containerFinalImage.append(img);
          } else {
            image.classList.remove("ag-is-image-selected");
            image.classList.remove("ag-is-choice-image-check");
          }
        });
      });
    });
  }

  showPreviewImageChoice() {
    const btnConfirmPrev = document.querySelector(".ag-js-btn-choice-image");
    if (btnConfirmPrev) {
      btnConfirmPrev.addEventListener("click", () => {
        const modal = Array.from(
          document.querySelectorAll("[data-modal='show_select_image']")
        );

        modal.forEach(element => {
          if (element.classList.contains("ag-is-modal_visible")) {
            // Remove class visible of the modal
            element.classList.remove("ag-is-modal_visible");
          }
        });

        // Remove class overflow of the body
        document.querySelector("body").classList.remove("ag-is-overflow");
      });
    }
  }
}

tabsCover = new Tabs("ag-menu-bar__item_active", "ag-has-content-menu-hide");
