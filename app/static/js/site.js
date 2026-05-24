/** Navegação mobile e utilitários do site público */
(function () {
  const toggle = document.getElementById("navToggle");
  const nav = document.querySelector(".nav-main");
  if (!toggle || !nav) return;

  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });
})();
