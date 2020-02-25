export default {
    rawfiles: [
        { from: "common/images/", to: "images/" },
    ],
    bundles: {
        "main": [
            "common/expose_libs.ts",
            "common/_variables.scss",
            "common/index.scss",
            "common/cookieconsent/display-cookieconsent.ts",
            "common/icons-library.ts",
        ],
        "render-markdown": [
            "common/render-markdown.ts",
            "common/render-markdown.scss",
        ],
        "fullcalendar": [
            "common/fullcalendar.ts"
        ],
        "filtered-select-multiple-converter": [
            "common/filtered-select-multiple-converter.js"
        ],
        "consent-dialog": [
            "common/consent-dialog.ts"
        ]
    },
};
