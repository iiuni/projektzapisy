// Displays the data consent modal right when the page loads.
import * as bootstrap from "bootstrap";

window.onload = function() {
  const modal = document.getElementById('consentDialog');

  if (modal) {
    const bootstrapModal = new bootstrap.Modal(modal, {});
    bootstrapModal.show();
  }
};
