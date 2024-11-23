// import Swiper from 'swiper';
const Swiper = require("swiper/dist/js/swiper.min.js");

//- Slider Filter Home
var jsSliderFilter = new Swiper(".js-sliderFilter", {
  breakpoints: {
    400: {
      slidesPerView: 2
    },
    560: {
      slidesPerView: 3
    },
    768: {
      slidesPerView: 4
    },
    1024: {
      slidesPerView: 5
    }
  },
  breakpointsInverse: true,
  navigation: {
    nextEl: ".ag-has-slider_primary_next",
    prevEl: ".ag-has-slider_primary_prev"
  },
  pagination: {
    el: ".ag-has-slider_primary__dots",
    clickable: true,
    dynamicBullets: true,
    renderBullet: function(index, className) {
      return (
        '<button class="' +
        className +
        ' ag-c-slider__bullet" type="button">' +
        "</button>"
      );
    }
  },
  slidesPerView: 1
});

var jsSliderSourceInformation = new Swiper(".js-sliderSourceInformation", {
  breakpoints: {
    500: {
      slidesPerView: 2
    },
    768: {
      slidesPerView: 3
    }
  },
  watchOverflow: true,
  breakpointsInverse: true,
  navigation: {
    nextEl: ".ag-has-slider_contrast__next",
    prevEl: ".ag-has-slider_contrast__prev"
  },
  pagination: {
    el: ".ag-has-slider_contrast__dots",
    clickable: true,
    dynamicBullets: true,
    renderBullet: function(index, className) {
      return (
        '<button class="' +
        className +
        ' ag-c-slider__bullet" type="button">' +
        "</button>"
      );
    }
  },
  slidesPerView: 1
});

//- Slider Home : c07_slider => .ag-c-slider_box
new Swiper(".ag-js-slider-home", {
  navigation: {
    nextEl: ".ag-has-slider_box_next",
    prevEl: ".ag-has-slider_box_prev"
  },
  pagination: {
    el: ".ag-has-slider_box__dots",
    clickable: true,
    dynamicBullets: true,
    renderBullet: function(index, className) {
      return (
        '<button class="' +
        className +
        ' ag-c-slider__bullet" type="button">' +
        "</button>"
      );
    }
  },
  slidesPerView: 1,
  watchOverflow: true
});

new Swiper(".js-hero-slider", {
  navigation: {
    nextEl: ".ag-has-slider_box_next",
    prevEl: ".ag-has-slider_box_prev"
  },
  pagination: {
    el: ".js-hero-pagination",
    clickable: true,
    dynamicBullets: true,
    renderBullet: function(index, className) {
      return (
        '<button class="' +
        className +
        ' ag-c-slider__bullet ag-c-slider__bullet_primary" type="button">' +
        "</button>"
      );
    }
  },
  slidesPerView: 1,
  watchOverflow: true,
  on: {
    init: function() {
      identifySlideType(this);
    },
    slideChange: function() {
      setTimeout(() => {
        identifySlideType(this);
      }, 50);
    }
  }
});

function identifySlideType(el) {
  const slideActive = el.$wrapperEl[0].querySelector(".swiper-slide-active");

  if (slideActive) {
    const targetHero = slideActive.closest(".js-hero-slider");
    const slideBg = slideActive.querySelector(".js-slider-background");
    const classHeroBg = "is-hero-bg";

    if (slideBg) {
      const bgImage = slideBg.dataset.backgroundImage;

      targetHero.setAttribute("style", `background-image:url(${bgImage});`);
      targetHero.classList.add(classHeroBg);
    } else {
      targetHero.setAttribute("style", "");
      targetHero.classList.remove(classHeroBg);
    }
  }
}

// Slider Exposiciones
var sliderExposition = new Swiper(".ag-js-slider-exposition", {
  navigation: {
    nextEl: ".ag-c-slider__control_next",
    prevEl: ".ag-c-slider__control_prev"
  },
  watchOverflow: true,
  pagination: {
    el: ".ag-c-slider__dots",
    clickable: true,
    dynamicBullets: true,
    renderBullet: function(index, className) {
      return (
        '<button class="' +
        className +
        ' ag-c-slider__bullet" type="button">' +
        "</button>"
      );
    }
  },
  slidesPerView: 1,
  autoHeight: true
});

// Slider Modal Exposiciones [Galería de imágenes]
var sliderModalExpoGallery = new Swiper(".ag-js-slider-modal", {
  slidesPerView: 1,
  spaceBetween: 70,
  navigation: {
    nextEl: ".ag-c-slider-grid__control_next",
    prevEl: ".ag-c-slider-grid__control_prev"
  },
  pagination: {
    el: ".ag-has-slider-grid__counter",
    clickable: true,
    type: "custom",
    renderCustom: function(sliderModalExpoGallery, current, total) {
      return current + "<small> de </small>" + total;
    }
  },
  breakpoints: {
    640: {
      spaceBetween: 20
    }
  }
});

//- Slider Gallery Home : c08_slider-gallery
var sliderGallery = new Swiper(".ag-js-slider-gallery", {
  // init: false,
  effect: "coverflow",
  grabCursor: true,
  centeredSlides: true,
  slidesPerView: "auto",
  loop: true,
  coverflowEffect: {
    rotate: 0,
    stretch: -100,
    depth: 400,
    modifier: 1,
    slideShadows: false
  },
  navigation: {
    nextEl: ".ag-js-slider-gallery .ag-has-slider-gallery__control_next",
    prevEl: ".ag-js-slider-gallery .ag-has-slider-gallery__control_prev"
  },
  pagination: {
    el: ".ag-js-slider-gallery .ag-has-slider-gallery__dots",
    clickable: true,
    dynamicBullets: true,
    renderBullet: function(index, className) {
      return (
        '<button class="' +
        className +
        ' ag-c-slider__bullet" type="button">' +
        "</button>"
      );
    }
  }
});

const changeTabIndexHomeGallery = function() {
  const sliderGalleryHomeElem = document.getElementsByClassName(
    "ag-js-slider-gallery"
  )[0];
  if (!sliderGalleryHomeElem) return;
  const slides = Array.from(
    sliderGalleryHomeElem.getElementsByClassName("swiper-slide")
  );
  const activeSlide = sliderGalleryHomeElem.getElementsByClassName(
    "swiper-slide-active"
  )[0];
  const elementsTabIndex = Array.from(
    activeSlide.querySelectorAll("[tabindex]")
  );
  slides.forEach(slide => {
    slide.setAttribute("tabindex", "-1");
    const contentTabindex = Array.from(slide.querySelectorAll("[tabindex]"));
    contentTabindex.forEach(elem => {
      elem.setAttribute("tabindex", "-1");
    });
  });
  activeSlide.setAttribute("tabindex", "0");
  elementsTabIndex.forEach(elem => {
    elem.setAttribute("tabindex", "0");
  });
};

changeTabIndexHomeGallery();

sliderGallery.on("slideChangeTransitionEnd", function() {
  changeTabIndexHomeGallery();
});

//- Slider banner Sets : set_banner.html
const sliderSetElement = document.getElementsByClassName("ag-js-sliderSet")[0];
if (sliderSetElement) {
  if (sliderSetElement.getElementsByClassName("swiper-slide").length > 1) {
    new Swiper(".ag-js-sliderSet", {
      slidesPerView: "auto",
      paginationClickable: true,
      spaceBetween: 110,
      allowTouchMove: false,
      centeredSlides: true,
      watchOverflow: true,
      watchSlidesProgress: true,
      focusableElements: ["a"],
      simulateTouch: false,
      navigation: {
        nextEl: ".ag-c-slider__control_next",
        prevEl: ".ag-c-slider__control_prev"
      },
      breakpoints: {
        1024: {
          allowTouchMove: true,
          simulateTouch: true
        }
      }
    });
  } else {
    const sliderControls = sliderSetElement.getElementsByClassName(
      "ag-c-slider__control"
    );
    for (let i = 0; i < sliderControls.length; i++) {
      sliderControls[i].style.display = "none";
    }
  }
}

//- Skydrop Home : b12_skydrop
var skydrop;
const createSkydrop = function() {
  skydrop = new Swiper(".js-sliderTablet", {
    breakpointsInverse: true,
    // init: true,
    slidesPerView: 1,
    breakpoints: {
      650: {
        slidesPerView: 2
      }
    },
    spaceBetween: 25
  });
  if (window.innerWidth > 1024) {
    skydrop.destroy(true, true);
  }
};

//- Slider Related Cards
var sliderRelatedCard;

const createSliderRelatedCard = function() {
  const itemRelatedCard = document.querySelectorAll(".ag-js-relatedCardItem");
  const wrapRelatedCard = document.querySelector(".js-wrapSliderRelatedCard");
  const counterItemRelatedCard = itemRelatedCard.length;

  if (counterItemRelatedCard > 2) {
    wrapRelatedCard.classList.remove("ag-l-inner-inside");
    wrapRelatedCard.classList.add("ag-c-related-cards__inner");
    sliderRelatedCard = new Swiper(".js-sliderRelatedCard", {
      spaceBetween: 6,
      slidesPerView: "auto",
      centeredSlides: true,
      loop: true,
      breakpoints: {
        1280: {
          spaceBetween: 16
        }
      },
      a11y: {
        prevSlideMessage: "Exposición anterior",
        nextSlideMessage: "Próxima Exposición"
      },
      navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
        disabledClass: "disabled_swiper_button"
      },
      pagination: {
        el: ".ag-has-related-cards__counter",
        clickable: true,
        type: "custom",
        bulletElement: "span",
        renderCustom: function(index, current, total) {
          return (
            current +
            "<small> de </small>" +
            total +
            "<span>Exposiciones sugeridas</span>"
          );
        }
      }
    });
  }

  if (window.innerWidth < 767) {
    sliderRelatedCard.destroy(true, true);
  }
};

document.getElementsByClassName("js-sliderTablet")[0] && createSkydrop();
document.getElementsByClassName("js-sliderRelatedCard")[0] &&
  createSliderRelatedCard();

window.addEventListener("resize", () => {
  if (skydrop) {
    if (!skydrop.destroyed && window.innerWidth >= 1024) {
      skydrop.destroy(true, true);
    } else if (skydrop.destroyed) {
      createSkydrop();
    }
  }
  if (sliderRelatedCard) {
    if (!sliderRelatedCard.destroyed && window.innerWidth < 767) {
      sliderRelatedCard.destroy(true, true);
    } else if (sliderRelatedCard.destroyed) {
      createSliderRelatedCard();
    }
  }
});

// Slider Modal Exposiciones [Galería de imágenes y Vídeos]

function getPageDefaultSwiperConfig() {
  return {
    slidesPerView: "auto",
    paginationClickable: true,
    centeredSlides: true,
    loop: true,
    navigation: {
      nextEl: ".ag-c-slider-grid__control_next",
      prevEl: ".ag-c-slider-grid__control_prev"
    },
    pagination: {
      el: ".ag-has-slider-grid__dots",
      clickable: true,
      dynamicBullets: true,
      renderBullet: function(index, className) {
        return (
          '<button class="' +
          className +
          ' ag-c-slider-grid__bullet" type="button">' +
          (index + 1) +
          "</button>"
        );
      }
    }
  };
}

function getPageImgSwiperConfig(id) {
  const config = getPageDefaultSwiperConfig();
  config.navigation = {
    nextEl: `#page_img_swiper_control_next-${id}`,
    prevEl: `#page_img_swiper_control_prev-${id}`
  };
  config.pagination.el = `#page_img_swiper_pagination-${id}`;
  return config;
}

function getPageVideoSwiperConfig(id) {
  const config = getPageDefaultSwiperConfig();
  config.navigation = {
    nextEl: `#page_video_swiper_control_next-${id}`,
    prevEl: `#page_video_swiper_Control_prev-${id}`
  };
  config.pagination.el = `#page_video_swiper_pagination-${id}`;
  return config;
}

function getModalDefaultSwiperConfig() {
  return {
    slidesPerView: 1,
    spaceBetween: 70,
    autoHeight: true,
    navigation: {
      nextEl: ".ag-c-slider-grid__control_next",
      prevEl: ".ag-c-slider-grid__control_prev"
    },
    pagination: {
      el: ".ag-has-slider-grid__counter",
      clickable: true,
      type: "custom",
      renderCustom: function(swiper, current, total) {
        return current + "<small> de </small>" + total;
      }
    },
    breakpoints: {
      640: {
        spaceBetween: 20
      }
    }
  };
}

function getModalImgSwiperConfig(id) {
  const config = getModalDefaultSwiperConfig();
  config.navigation = {
    nextEl: `#modal_img_swiper_control_next-${id}`,
    prevEl: `#modal_img_swiper_control_prev-${id}`
  };

  config.pagination.el = `#modal_img_swiper_pagination-${id}`;
  return config;
}

function getModalVideoSwiperConfig(id) {
  const config = getModalDefaultSwiperConfig();
  config.navigation = {
    nextEl: `#modal_video_swiper_control_next-${id}`,
    prevEl: `#modal_video_swiper_control_prev-${id}`
  };

  config.pagination.el = `#modal_video_swiper_pagination-${id}`;
  return config;
}

function addOpenModalEvents(
  pageSwiperContainer,
  modalSwiper,
  openModalElementClassName
) {
  const swiperOnModal = modalSwiper;

  pageSwiperContainer
    .querySelectorAll(openModalElementClassName)
    .forEach(el => {
      const modalSwiper = swiperOnModal;
      if (!el.onclick) {
        el.onclick = function() {
          modalSwiper.slideTo(this.dataset.itemGalleryIndex);
        };
      }
    });
}

function handlePageSwiperContainer(
  pageSwiperContainer,
  pageSwiperConfig,
  modalSwiper,
  openModalElementClassName
) {
  var pageSwiper;
  addOpenModalEvents(
    pageSwiperContainer,
    modalSwiper,
    openModalElementClassName
  );

  if (window.innerWidth < 1024) {
    pageSwiper = new Swiper(pageSwiperContainer, pageSwiperConfig);
    addOpenModalEvents(
      pageSwiperContainer,
      modalSwiper,
      openModalElementClassName
    );
  }

  window.addEventListener("resize", function() {
    if (this.innerWidth >= 1024 && pageSwiper && !pageSwiper.destroyed) {
      pageSwiper.destroy(true, true);
      return;
    }

    if (
      this.innerWidth < 1024 &&
      (!pageSwiper || (pageSwiper && pageSwiper.destroyed))
    ) {
      pageSwiper = new Swiper(pageSwiperContainer, pageSwiperConfig);
      addOpenModalEvents(
        pageSwiperContainer,
        modalSwiper,
        openModalElementClassName
      );
    }
  });
}

function handleStopVideoPassingSlider() {
  let controlsSlider = document.querySelectorAll(".ag-js-slider-grid-control");
  controlsSlider.forEach(currentControl => {
    currentControl.addEventListener("click", e => {
      let parentSlider = e.target.closest(".ag-js-videoSliderModal");
      getPostMessageForStopVideo(parentSlider);
    });
  });
}

function handleStopVideosOnModalClose(modalContainer) {
  modalContainer.querySelectorAll(".ag-js-modalClose").forEach(closeBtn => {
    closeBtn.addEventListener("click", () => {
      getPostMessageForStopVideo(modalContainer);
    });
  });
}

/**
 * Get post message for stop video
 * @param {string} container Parent element of video slider
 */
function getPostMessageForStopVideo(container) {
  container.querySelectorAll("iframe").forEach(videoIframe => {
    videoIframe.contentWindow.postMessage(
      '{"event":"command","func":"' + "stopVideo" + '","args":""}',
      "*"
    );
  });
}

function expoGallerySlidersInit() {
  const imgPageGallerySliders = document.querySelectorAll(
    ".ag-js-imageSliderGrid"
  );

  imgPageGallerySliders.forEach(pageSwiperContainer => {
    const modalSwiper = new Swiper(
      `.ag-js-imgSliderModal[data-id="${pageSwiperContainer.dataset.id}"]`,
      getModalImgSwiperConfig(pageSwiperContainer.dataset.id)
    );
    handlePageSwiperContainer(
      pageSwiperContainer,
      getPageImgSwiperConfig(pageSwiperContainer.dataset.id),
      modalSwiper,
      ".ag-js-openImgGalleryModal"
    );
  });

  const videoPageGallerySliders = document.querySelectorAll(
    ".ag-js-videoSliderGrid"
  );

  videoPageGallerySliders.forEach(pageSwiperContainer => {
    const modalSwiperContainer = document.querySelector(
      `.ag-js-videoSliderModal[data-id="${pageSwiperContainer.dataset.id}"]`
    );

    const modalSwiper = new Swiper(
      modalSwiperContainer,
      getModalVideoSwiperConfig(pageSwiperContainer.dataset.id)
    );
    handlePageSwiperContainer(
      pageSwiperContainer,
      getPageVideoSwiperConfig(pageSwiperContainer.dataset.id),
      modalSwiper,
      ".ag-js-openVideoGalleryModal"
    );

    modalSwiperContainer.getElementsByTagName("iframe").forEach(videoIframe => {
      videoIframe.setAttribute(
        "src",
        videoIframe.getAttribute("src") + "&enablejsapi=1"
      );
    });

    handleStopVideosOnModalClose(modalSwiperContainer.closest(".ag-js-modal"));
  });

  handleStopVideoPassingSlider();
}

expoGallerySlidersInit();
