/*  This is a FontAwesome icon library for System Zapisów.
    To use a new icon, find it in a cheatsheet
    https://fontawesome.com/cheatsheet and add it to our collection. It can be
    used in any template in the project, just like with the typical FontAwesome
    set-up, except we do not include all the icons.
*/
import { library, dom } from "@fortawesome/fontawesome-svg-core";

import { faExternalLinkAlt } from "@fortawesome/free-solid-svg-icons/faExternalLinkAlt";
import { faBell as fasBell } from "@fortawesome/free-solid-svg-icons/faBell"
import { faBell as farBell } from "@fortawesome/free-regular-svg-icons/faBell"
library.add(faExternalLinkAlt);
library.add(fasBell, farBell);

// This allows us to include an icon with <i class="fa fa-[ICON-NAME]"></i>.
dom.watch();
