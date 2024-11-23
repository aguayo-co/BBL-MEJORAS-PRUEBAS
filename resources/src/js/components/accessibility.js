const dropdown = Array.from(
  document.getElementsByClassName("ag-js-dropdownSlide")
);

const addEventsTabAgHide = function(elements) {
  elements.forEach(elem => {
    elem.addEventListener("focus", function() {
      elem.closest(".ag-js-dropdownSlide").classList.remove("ag-is-hidden");
    });
    elem.addEventListener("blur", function() {
      elem.closest(".ag-js-dropdownSlide").classList.add("ag-is-hidden");
    });
  });
};

dropdown.forEach(elem => {
  const a = Array.from(elem.getElementsByTagName("a"));
  addEventsTabAgHide(a);

  const li = Array.from(elem.getElementsByTagName("li"));
  addEventsTabAgHide(li);
});
