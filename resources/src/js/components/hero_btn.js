(function() {
  const ButtonClassName = "c-hero__footer-btn";
  const Button = document.getElementsByClassName(ButtonClassName)[0];
  if (Button) {
    Button.addEventListener("click", function(e) {
      e.preventDefault();
      const destino = document.getElementById("scroll-down-to-first-content");
      const topPos = destino.offsetTop;
      document.documentElement.scrollTop = topPos;
    });
  }
})();
