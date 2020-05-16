export default {
    rawfiles: [
        { from: "images/", to: "../images/" },
    ],
    bundles: {
        "main": [
            "main/expose_libs.ts",
            "main/_variables.scss",
            "main/index.scss",
            "cookieconsent/display-cookieconsent.ts",
            "main/icons-library.ts",
            "main/sidebar-fold.js",
        ],
        "render-markdown": [
            "markdown/render-markdown.ts",
            "markdown/render-markdown.scss",
        ],
        "markdown-editor": [
            "markdown/markdown-editor.js",
        ],
    },
};
