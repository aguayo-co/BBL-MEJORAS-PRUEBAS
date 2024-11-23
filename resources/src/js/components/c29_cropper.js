// Import cropper from dir NodeJS
import Cropper from "cropperjs";

function uploadImage() {
  const inputUploadImage = document.querySelector("[name='upload_image']");
  if (inputUploadImage) {
    let reader = new FileReader();
    let preview = document.querySelector(".ag-js-preview-image");
    let image = "";

    inputUploadImage.addEventListener("change", e => {
      // Read charged file
      reader.readAsDataURL(e.target.files[0]);

      // When the file is check
      reader.onload = () => {
        // Add name for the final image
        var titleImage = e.target.files[0].name;

        document.querySelector(
          ".ag-js-imageUploadedName"
        ).innerHTML = titleImage;

        // Set data for image
        image = document.createElement("img");
        image.src = reader.result;
        image.classList.add("ag-is-cropper-img");
        image.classList.add("ag-js-img-crop");

        // Show img charged
        preview.innerHTML = "";
        preview.append(image);

        if (image.src) {
          if (image.closest(".ag-js-parent-cropper-profile")) {
            showCropper(4, 4);
          } else {
            showCropper(16, 9);
          }
        }
      };
    });
  }
}

function showCropper(x, y) {
  const imageCrop = document.querySelector(".ag-js-img-crop");

  const cropper = new Cropper(imageCrop, {
    aspectRatio: x / y,
    background: false,
    ready: () => {
      zoom();
      rotate();
      move();
      cropImage();
    }
  });

  function rotate() {
    const rotateRight = document.querySelector(".ag-js-right");
    const rotateLeft = document.querySelector(".ag-js-left");

    rotateRight.addEventListener("click", () => {
      cropper.rotate(45);
    });

    rotateLeft.addEventListener("click", () => {
      cropper.rotate(-45);
    });
  }

  function zoom() {
    const zoomIn = document.querySelector(".ag-js-zoomIn");
    const zoomOut = document.querySelector(".ag-js-zoomOut");

    zoomIn.addEventListener("click", () => {
      cropper.zoom(0.1);
    });
    zoomOut.addEventListener("click", () => {
      cropper.zoom(-0.1);
    });
  }

  function move() {
    const moveTop = document.querySelector(".ag-js-move-top");
    const moveRight = document.querySelector(".ag-js-move-right");
    const moveDown = document.querySelector(".ag-js-move-down");
    const moveLeft = document.querySelector(".ag-js-move-left");

    moveTop.addEventListener("click", () => {
      cropper.move(-1, -10);
    });

    moveRight.addEventListener("click", () => {
      cropper.move(10, 0);
    });

    moveDown.addEventListener("click", () => {
      cropper.move(1, 10);
    });

    moveLeft.addEventListener("click", () => {
      cropper.move(-10, 0);
    });
  }

  function cropImage() {
    const buttonCrop = document.querySelector(".ag-js-crop-image");
    const containerImgShow = document.querySelector(".ag-js-fileUpload");
    const modal = Array.from(
      document.querySelectorAll("[data-modal='show_select_image']")
    );
    const containerFinalImage = document.querySelector(".ag-js-img-croped");

    buttonCrop.addEventListener("click", () => {
      const canvas = cropper.getCroppedCanvas();
      const base64encodedImage = canvas.toDataURL("image/jpeg, 0.7");
      const img = document.createElement("img");
      // Show container for image in the form
      containerImgShow.style.display = "flex";

      modal.forEach(element => {
        if (element.classList.contains("ag-is-modal_visible")) {
          // Remove class visible of the modal
          element.classList.remove("ag-is-modal_visible");
        }
      });

      // Remove class overflow of the body
      document.querySelector("body").classList.remove("ag-is-overflow");

      if (containerFinalImage.children.length > 0) {
        containerFinalImage.removeChild(
          document.querySelector(".ag-js-croped-img")
        );
      }

      //Set data for show crop image in the form
      img.setAttribute("src", base64encodedImage);
      img.classList.add("ag-is-cropper-img-croped");
      img.classList.add("ag-js-croped-img");
      containerFinalImage.append(img);

      // Set value for cropped_image field
      document.querySelector("#id_cropped_image").value = base64encodedImage;
    });
  }
}

uploadImage();
