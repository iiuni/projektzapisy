export default {
    rawfiles: [
        { from: "legacy/css/", to: "css/" },
        { from: "legacy/help/", to: "help/" },
        { from: "legacy/images/", to: "images/" },
        { from: "legacy/js/", to: "js/" },
        { from: "legacy/vendor/", to: "vendor/" },
        { from: "legacy/favicon.ico", to: "favicon.ico" },
        { from: "legacy/feed-icon.png", to: "feed-icon.png" },
    ],
    bundles: {
        "main": [
            "common/expose_libs.ts",
            "common/_variables.scss",
            "common/index.scss",
            "common/cookieconsent/display-cookieconsent.ts",
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
