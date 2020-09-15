import * as $ from "jquery";
import * as Popper from "popper.js";

(window as any).$ = $;
(window as any).jQuery = $;
(window as any).Popper = Popper;

import "bootstrap";

$(function () {
  // Enable Bootstrap popovers on entire site.
  $('[data-toggle="popover"]').popover();
});
