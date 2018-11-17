import * as path from "path";
import * as fs from "fs";
import * as glob from "glob";
import * as os from "os";

import { getVueCssLoaders, parseBool } from "./webpack-utils";
import * as webpack from "webpack";
import ForkTsCheckerWebpackPlugin from "fork-ts-checker-webpack-plugin";
import HappyPack from "happypack";
import { BundleAnalyzerPlugin } from "webpack-bundle-analyzer";
const BundleTracker = require("webpack-bundle-tracker");
const ExtractTextPlugin = require("extract-text-webpack-plugin");
const CleanWebpackPlugin = require("clean-webpack-plugin");
const SpeedMeasurePlugin = require("speed-measure-webpack-plugin");
const UglifyJSPlugin = require("uglifyjs-webpack-plugin");
const WebpackShellPlugin = require("webpack-shell-plugin");

// Leave one cpu free for the ts type checker...
const happyThreadPool = HappyPack.ThreadPool({
	// ...but make sure we spawn at least one thread
	size: Math.max(os.cpus().length - 1, 1)
});

const smp = new SpeedMeasurePlugin();

let DEV: boolean;
switch (process.env.NODE_ENV) {
	case "development":
		DEV = true;
		break;
	case "production":
		DEV = false;
		break;
	default:
		throw new Error(`Bad NODE_ENV ${process.env.NODE_ENV}`);
}

const BUNDLE_OUTPUT_DIR = "compiled_assets";
const ASSET_DIR = "assets";
const ASSET_DEF_FILENAME = "asset-defs.ts";
const ASSET_DEF_SEARCH_DIR = "apps";

type RawfileDef = {
	from: string,
	to: string
};

type AssetDefs = {
	bundles?: {
		[key: string]: string[],
	},
	rawfiles?: Array<RawfileDef | string>
};

type FinalAssetDefs = {
	bundles?: {
		[key: string]: string[],
	},
	rawfiles?: RawfileDef[],
};

function mergeAssetDefs(defs: AssetDefs, newDefs: AssetDefs): AssetDefs {
	defs.bundles = defs.bundles || {};
	defs.rawfiles = defs.rawfiles || [];
	Object.assign(defs.bundles, newDefs.bundles);
	defs.rawfiles = defs.rawfiles.concat(newDefs.rawfiles || []);
	return defs;
}

function getFileInputPath(packageDir: string, packageFilePath: string): string {
	if (path.isAbsolute(packageFilePath)) {
		return packageFilePath;
	}
	// All relative paths are assumed to be in ASSET_DIR, so check if it exists
	// and throw a friendly message if it doesn't
	const packageAssetDirPath = path.resolve(packageDir, ASSET_DIR);
	if (!fs.existsSync(packageAssetDirPath)) {
		throw new Error(
			`${packageAssetDirPath} does not exist. ` +
			`Create it and put your assets for this app there.`);
	} else if (!fs.lstatSync(packageAssetDirPath).isDirectory()) {
		throw new Error(
			`${packageAssetDirPath} is not a directory. ` +
			`It should be a directory containing all your assets for this app`);
	}
	return path.resolve(packageDir, ASSET_DIR, packageFilePath);
}

function processDefs(defs: AssetDefs, packageName: string, packageDir: string): FinalAssetDefs {
	const result: FinalAssetDefs = {
		bundles: {},
		rawfiles: [],
	};
	for (const bundle in defs.bundles || {}) {
		const fullName = packageName.length ? `${packageName}-${bundle}` : bundle;
		result.bundles![fullName] = defs.bundles![bundle].map(filepath => {
			return getFileInputPath(packageDir, filepath);
		});
	}
	result.rawfiles = (defs.rawfiles || []).map(rawfileDef => {
		if (typeof rawfileDef === "string") {
			rawfileDef = {
				from: rawfileDef,
				to: rawfileDef,
			};
		}
		const getRawfileOutputPath = (rawfilePath: string) => {
			return path.resolve(BUNDLE_OUTPUT_DIR, packageName, rawfilePath);
		};
		return {
			from: getFileInputPath(packageDir, rawfileDef.from),
			to: getRawfileOutputPath(rawfileDef.to),
		};
	});
	return result;
}

function readAsssetDefsFromFile(filepath: string): AssetDefs {
	const dirPath = path.dirname(filepath);
	const dirName = path.basename(dirPath);
	const defs: AssetDefs = require(path.resolve(filepath)).default;
	const packageName = dirName !== "." ? dirName : "";
	return processDefs(defs, packageName, dirPath);
}

function getAllAssetDefs() {
	const result: FinalAssetDefs = {
		bundles: {},
		rawfiles: [],
	};
	if (fs.existsSync(ASSET_DEF_FILENAME)) {
		const defs = readAsssetDefsFromFile(ASSET_DEF_FILENAME);
		mergeAssetDefs(result, defs);
	}
	const searchPath = path.join(ASSET_DEF_SEARCH_DIR, "**", ASSET_DEF_FILENAME);
	for (const defFile of glob.sync(searchPath)) {
		const defs = readAsssetDefsFromFile(defFile);
		mergeAssetDefs(result, defs);
	}
	return result;
}

function buildCopyCommandsForRawfiles(rawfiles: RawfileDef[]): string[] {
	return (rawfiles || []).map(r => {
		return `cp -r ${r.from} ${r.to}`;
	});
}

const allAssetDefs = getAllAssetDefs();
console.log(allAssetDefs);

const copyCommands = buildCopyCommandsForRawfiles(allAssetDefs.rawfiles);

const webpackConfig: webpack.Configuration = {
	entry: Object.assign({
		polyfill: "babel-polyfill",
	}, allAssetDefs.bundles),
	output: {
		path: path.resolve(BUNDLE_OUTPUT_DIR),
		filename: DEV ? "[name]_[hash].js" : "[name]_[hash].min.js",
	},
	watchOptions: {
		poll: 2000
	},
	// Webpack types don't seem to be aware of this devtool
	devtool: DEV ? "inline-cheap-module-source-map" as any : false,
	mode: DEV ? "development" : "production",
	optimization: {
		// This is only applied if optimization.minimize is true (mode === "development")
		minimizer: [
			new UglifyJSPlugin({
				sourceMap: false,
				parallel: true,
				uglifyOptions: {
					compress: true,
					output: { comments: false },
					comments: false,
					ecma: 5,
					mangle: {
						toplevel: true,
						eval: true,
					},
					hoist_funs: true,
				},
			}),
		],
		splitChunks: {
			cacheGroups: {
			  	commons: {
					name: "commons",
					filename: "common_chunks.js",
					chunks: "initial",
					minChunks: 2
			  	}
			},
		},
	},
	module: {
		rules: [
			// TypeScript source:
			// 1) tsc: TS -> ES6
			// 2) babel: ES6 -> ES5 (and polyfilling)
			{
				// This doesn't use happypack because for whatever reason appendTsSuffixTo
				// (needed by vuejs) breaks it
				test: /\.tsx?$/,
				use: [
					{
						loader: "cache-loader",
						query: {
							cacheDirectory: path.resolve("node_modules/.cache-loader-tsbabel")
						}
					},
					{ loader: "babel-loader" },
					{
						loader: "ts-loader",
						query: {
							appendTsSuffixTo: [/\.vue$/],
							transpileOnly: true,
						}
					}
				],
				exclude: /node_modules/,
			},
			// ES6 source: babel converts to ES5 (and polyfills)
			{
				test: /\.jsx?$/,
				loader: "happypack/loader?id=babel",
				exclude: /node_modules/
			},
			{
				test: /\.vue$/,
				loader: "vue-loader",
				options: {
					loaders: getVueCssLoaders(
						DEV ? {
							sourceMap: true,
							extract: false,
						} : {
							sourceMap: false,
							extract: true,
							minifyCss: true,
						}
					),
					esModule: true,
					postcss: [
					  require("autoprefixer")({
						browsers: ["last 2 versions"]
					  })
					],
				},
			},
			{
				test: /\.less$/,
				use: ExtractTextPlugin.extract({
					fallback: "style-loader",
					use: [{
						loader: "css-loader",
						options: { minimize: !DEV }
					}, {
						loader: "less-loader"
					}]
				})
			},
			{
				test: /\.s[c|a]ss$/,
				use: ExtractTextPlugin.extract({
					fallback: "style-loader",
					use: [{
						loader: "css-loader",
						options: { minimize: !DEV }
					}, {
						loader: "sass-loader"
					}]
				})
			},
			{
				test: /\.css$/,
				use: ExtractTextPlugin.extract({
					fallback: "style-loader",
					use: [{
						loader: "css-loader",
						options: { minimize: !DEV }
					}]
				})
			},
			{
				test: /\.(png|jpg|gif)$/,
				use: [{
					loader: "url-loader",
					options: {
						limit: 8192,
						// ACHTUNG this should match the value of STATIC_URL in settings.py
						publicPath: "/static",
					}
				}]
			}
		]
	},
	resolve: {
		modules: [
			path.resolve(ASSET_DIR),
			path.resolve("./node_modules"),
		],
		extensions: [".ts", ".js", ".vue", ".tsx", ".png", ".jpg", ".gif"],
		alias: {
			"vue$": "vue/dist/vue.runtime.esm.js",
		},
	},
	resolveLoader: {
		modules: [
			path.resolve("./node_modules"),
		],
	},
	plugins: [
		new CleanWebpackPlugin([path.resolve(BUNDLE_OUTPUT_DIR)], {
			verbose:  true,
			dry:      false,
			root:	  process.cwd(),
		}),
		new ExtractTextPlugin("[name]-[hash].min.css", {
			allChunks: true
		}),
		new BundleTracker({ filename: "webpack_resources/webpack-stats.json" }),
		// This will copy "raw" assets - ones where we don't want any transformations
		// (e.g. bootstrap styles)
		// We're not using copy-webpack-plugin because that tries to determine
		// which files changed in watch mode and it takes forever (around 30 seconds)
		// due to the slow shared filesystem we're using
		new WebpackShellPlugin({
			onBuildEnd: [
				"echo Copying static assets...",
				...copyCommands,
			],
			// If this is set, the command won't be run on incremental builds in watch mode
			// (matters for performance)
			dev: DEV,
		}),
		new HappyPack({
			id: "babel",
			threadPool: happyThreadPool,
			loaders: [
				{
					loader: "cache-loader",
					query: {
						cacheDirectory: path.resolve("node_modules/.cache-loader-babel")
					}
				},
				{ loader: "babel-loader" },
			],
		}),
		new ForkTsCheckerWebpackPlugin({ checkSyntacticErrors: true }),
	],
};

if (parseBool(process.env.ANALYZE)) {
	console.info("Will perform bundle analysis");
	webpackConfig.plugins.push(new BundleAnalyzerPlugin({
		analyzerMode: "server",
		analyzerHost: "0.0.0.0",
		analyzerPort: "8000",
	}));
}

module.exports = webpackConfig;
