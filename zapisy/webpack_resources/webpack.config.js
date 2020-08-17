'use strict'
const path = require("path");
const autoprefixer = require("autoprefixer");

const BundleTracker = require("webpack-bundle-tracker");
const {
  CleanWebpackPlugin,
} = require("clean-webpack-plugin");
const VueLoaderPlugin = require("vue-loader/lib/plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const MomentLocalesPlugin = require("moment-locales-webpack-plugin");

const DEV_MODE = process.env.NODE_ENV !== "production";

const BUNDLE_OUTPUT_DIR = "compiled_assets";
const ASSET_DEF_SEARCH_DIR = "apps";
const STATS_DIR = "webpack_resources";

const ASSET_DEFS = require(path.resolve(
  "webpack_resources/asset-defs.js"
));

// List containing all rules needed to compile all types of
// assets used in PZ. If needed, new rules can be easily appended
// to the end of this list.
const RULES = [
  // Vue files rule
  {
    test: /\.vue$/,
    use: "vue-loader",
    exclude: /node_modules/,
  },

  // Typescript files rule
  {
    test: /\.tsx?$/,
    loader: "ts-loader",
    options: { appendTsSuffixTo: [/\.vue$/] },
    exclude: /node_modules/,
  },

  // Javascript files rule
  {
    test: /\.js$/,
    exclude: /node_modules/,
    use: {
      loader: "babel-loader",
      options: {
        presets: [
          [
            "@babel/preset-env",
            {
              targets: {
                browsers: ["last 2 versions"],
              },
            },
          ],
        ],
        plugins: [
          "@babel/plugin-proposal-object-rest-spread",
        ],
      },
    },
  },

  // Styling files rule
  {
    test: /\.(sa|sc|c)ss$/,
    use: [
      MiniCssExtractPlugin.loader,
      {
        loader: "css-loader",
        options: { sourceMap: true },
      },
      {
        loader: "postcss-loader",
        options: {
          plugins: () => [autoprefixer()],
        },
      },
      "sass-loader",
    ],
  },

  // Other file assets rule
  {
    test: /.(jpg|png|woff(2)?|eot|ttf|svg)$/,
    loader: "file-loader",
  },
];

const PLUGINS = [
  new CleanWebpackPlugin(),
  new VueLoaderPlugin(),
  new BundleTracker({
    path: path.resolve(STATS_DIR),
    filename: "webpack-stats.json",
  }),
  new MiniCssExtractPlugin(),
  new MomentLocalesPlugin({
    localesToKeep: ["pl"],
  }),
];

const WEBPACK_CONFIG = {
  entry: ASSET_DEFS,
  output: {
    path: path.resolve(BUNDLE_OUTPUT_DIR),
    filename: DEV_MODE
      ? "[name]_[hash].js"
      : "[name]_[hash].min.js",
  },
  module: {
    rules: RULES,
  },
  optimization: {
    splitChunks: {
      cacheGroups: {
        vendors: {
          test: /node_modules/,
          chunks: "initial",
          name: "vendors",
          priority: 10,
          enforce: true,
        },
      },
      minChunks: 2,
    },
  },
  resolve: {
    modules: [path.resolve("./node_modules")],
    extensions: [
      ".ts",
      ".js",
      ".vue",
      ".jsx",
      ".tsx",
      ".png",
      ".jpg",
      ".gif",
      ".ico",
    ],
    alias: {
      vue$: "vue/dist/vue.runtime.esm.js",
      vuex$: "vuex/dist/vuex.esm.js",
      "@": path.resolve(ASSET_DEF_SEARCH_DIR),
    },
    mainFields: ["main", "module"],
  },
  plugins: PLUGINS,
  mode: DEV_MODE ? "development" : "production",
  devtool: DEV_MODE ? "cheap-eval-source-map" : false,
  watchOptions: {
    poll: 2000,
  },
};

module.exports = WEBPACK_CONFIG;
