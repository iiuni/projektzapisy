export default {
	rawfiles: [
		{ from: "legacy/css/", to: "css/" },
		{ from: "legacy/help/", to: "help/" },
		{ from: "legacy/images/", to: "images/" },
		{ from: "legacy/js/", to: "js/" },
		{ from: "legacy/vendor/", to: "vendor/" },
		{ from: "legacy/favicon.ico", to: "favicon.ico" },
		{ from: "legacy/feed-icon.png", to: "feed-icon.png" }
	],
	bundles: {
        "main": [
            "common/libs.ts",
		],
	},
};
