import "katex/dist/katex.css";
import "./katex.css";

import renderMathInElement from "katex/dist/contrib/auto-render";

document.addEventListener("DOMContentLoaded", () => {
  const element = document.getElementById("od-vote-main-rules")!;
  renderMathInElement(element);
});
