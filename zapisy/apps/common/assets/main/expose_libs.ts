import $ from "jquery";
import Popper from "popper.js";
import * as bootstrap from "bootstrap";

(window as any).$ = $;
(window as any).jQuery = $;
(window as any).Popper = Popper;

window.addEventListener("load", () => {
  Array.from(document.querySelectorAll('[data-bs-toggle="popover"]')).map(
    function (popoverTriggerEl) {
      return new bootstrap.Popover(popoverTriggerEl);
    }
  );
});
