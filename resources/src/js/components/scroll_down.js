(function() {
  const hideScrollButtonClassName = "ag-has-button-action_hidden";
  const scrollDownButtons = document.getElementsByClassName(
    "ag-js-button-scroll-down"
  );
  const scrollDownStaticButtons = document.getElementsByClassName(
    "ag-js-button-scroll-down-static"
  );
  scrollDownButtons.forEach(btn => {
    const scrollToElement = document.querySelector(".ag-is-button-scroll-stop");
    if (scrollToElement) {
      const handleIntersection = function(entries) {
        entries.forEach(entry => {
          if (
            entry.boundingClientRect.y < 0 ||
            (entry.intersectionRatio >= 0.5 && entry.boundingClientRect.y > 0)
          ) {
            btn.classList.add(hideScrollButtonClassName);
          }
          if (entry.intersectionRatio < 0.5 && entry.boundingClientRect.y > 0) {
            btn.classList.remove(hideScrollButtonClassName);
          }
        });
      };

      const observer = new IntersectionObserver(handleIntersection, {
        threshold: [0.5]
      });

      observer.observe(scrollToElement);

      btn.addEventListener("click", function() {
        scrollToElement.scrollIntoView({ behavior: "smooth" });
      });
    } else {
      btn.classList.add(hideScrollButtonClassName);
    }
  });
  scrollDownStaticButtons.forEach(btn => {
    const scrollToElement = document.querySelector(".ag-is-button-scroll-stop");
    if (scrollToElement) {
      btn.addEventListener("click", function() {
        scrollToElement.scrollIntoView({ behavior: "smooth" });
      });
    } else {
      btn.classList.add(hideScrollButtonClassName);
    }
  });
})();
