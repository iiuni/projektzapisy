import marked from "marked";

let callback = function(mutations, observer) {
    for (const element of document.querySelectorAll(".markdown")) {
        const raw = element.textContent;
        const rendered = marked(raw);
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
const targetNode = document.getElementById("main-content") ||
document.getElementById("main-content-container");
let observer = new MutationObserver(callback);
observer.observe(targetNode, config);
