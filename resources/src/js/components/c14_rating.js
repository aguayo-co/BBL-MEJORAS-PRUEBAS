const ratingInputs = Array.from(document.getElementsByName("rating"));
if (ratingInputs[0]) {
  ratingInputs.forEach((input, i) => {
    const ratingsContainer = document.getElementsByClassName(
      "ag-js-activeRatings"
    );
    input.addEventListener("change", function() {
      const activeRatings = Array.from(
        document.getElementsByClassName("ag-is-ratingAction")
      );
      activeRatings.forEach(rating => {
        rating.classList.remove("ag-is-ratingAction");
      });
      for (let index = 0; index < i; index++) {
        ratingsContainer[index].classList.add("ag-is-ratingAction");
      }
    });
  });
}
