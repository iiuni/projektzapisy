const merge = require("webpack-merge");
const common = require("./webpack.common.ts");

module.exports = merge(common({
	minifyCss: false,
	vueCssOptions: {
		sourceMap: true,
		extract: false,
	}
}), {
	devtool: "inline-source-map"
});
