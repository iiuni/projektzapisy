import MarkdownIt from "markdown-it";

const md = MarkdownIt({
  linkify: true,
  typographer: true,
  quotes: "„”«»",
});

let callback = function (_mutations: any, _observer: any) {
  for (const element of document.querySelectorAll(".markdown")) {
    const raw = element.textContent || "";
    const rendered = md.render(raw);
    element.innerHTML = rendered;
    // This way Markdown is not rendered twice.
    element.classList.remove("markdown");
    element.classList.add("markdown-rendered");
  }
};

// Options for the observer (which mutations to observe)
const config = { attributes: false, childList: true, subtree: false };
// Bind to either #main-content (a view with sidebar like the courses page) or
// #main-content-container (a full-page view like my-proposals).
const targetNode =
  document.getElementById("main-content") ||
  document.getElementById("main-content-container")!;
let observer = new MutationObserver(callback);
observer.observe(targetNode, config);
