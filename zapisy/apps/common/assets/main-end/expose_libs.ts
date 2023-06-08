import { Popover } from "bootstrap";

var popoverTriggerList = [].slice.call(
  document.querySelectorAll('[data-bs-toggle="popover"]')
);
popoverTriggerList.map(function (popoverTriggerEl) {
  console.log(popoverTriggerEl);
  return new Popover(popoverTriggerEl);
});
