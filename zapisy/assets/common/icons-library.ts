/*  This is a FontAwesome icon library for System Zapisów.
    To use a new icon, find it in a cheatsheet
    https://fontawesome.com/cheatsheet and add it to our collection. It can be
    used in any template in the project, just like with the typical FontAwesome
    set-up, except we do not include all the icons.
*/
import { library, dom } from "@fortawesome/fontawesome-svg-core";

import { faExternalLinkAlt } from "@fortawesome/free-solid-svg-icons/faExternalLinkAlt";
library.add(faExternalLinkAlt);

import { faPrint } from "@fortawesome/free-solid-svg-icons/faPrint";
library.add(faPrint);

import { faPlus } from "@fortawesome/free-solid-svg-icons/faPlus";
library.add(faPlus);

import { faMinus } from "@fortawesome/free-solid-svg-icons/faMinus";
library.add(faMinus);

// This allows us to include an icon with <i class="fa fa-[ICON-NAME]"></i>.
dom.watch();
