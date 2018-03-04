const merge = require("webpack-merge");
const UglifyJSPlugin = require("uglifyjs-webpack-plugin");
const ExtractTextPlugin = require("extract-text-webpack-plugin");
const common = require("./webpack.common.ts");
const webpack = require("webpack");

module.exports = merge(common({
	minifyCss: true,
	vueCssOptions: {
		sourceMap: false,
		extract: true,
		minifyCss: true,
	}
}), {
	plugins: [
		new webpack.DefinePlugin({
			"process.env": {
				NODE_ENV: "\"production\""
			}
		}),
		new UglifyJSPlugin({
			sourceMap: false,
			compress: true,
			output: { comments: false },
			comments: false,
			uglifyOptions: {
				ecma: 5,
				mangle: {
					toplevel: true,
					eval: true,
				},
				hoist_funs: true,
			},
		}),
	]
});
