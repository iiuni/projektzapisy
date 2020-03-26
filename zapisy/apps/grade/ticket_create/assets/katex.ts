import "katex/dist/katex.css";
import "./katex.less";

import renderMathInElement from "katex/dist/contrib/auto-render";

import { whenDomLoaded } from "common/utils";

whenDomLoaded(() => {
   const element = document.getElementById("od-vote-main-rules")!;
   renderMathInElement(element);
});