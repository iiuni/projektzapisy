"use strict";
const path = require("path");

const PnpWebpackPlugin = require(`pnp-webpack-plugin`);

const BundleTracker = require("webpack-bundle-tracker");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const ForkTsCheckerWebpackPlugin = require("fork-ts-checker-webpack-plugin");
const VueLoaderPlugin = require("vue-loader/lib/plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const MomentLocalesPlugin = require("moment-locales-webpack-plugin");

const DEV_MODE = process.env.NODE_ENV !== "production";

const BUNDLE_OUTPUT_DIR = "compiled_assets";
const ASSET_DEF_SEARCH_DIR = "apps";
const STATS_DIR = "webpack_resources";

const ASSET_DEFS = require(path.resolve("webpack_resources/asset-defs.js"));

// List containing all rules needed to compile all types of
// assets used in PZ. If needed, new rules can be easily appended
// to the end of this list.
const RULES = [
  // Vue files rule
  {
    test: /\.vue$/,
    use: require.resolve("vue-loader"),
    exclude: /node_modules/,
  },

  // Javascript files rule
  {
    test: /\.(ts|js)$/,
    exclude: /node_modules/,
    use: {
      loader: require.resolve("babel-loader"),
      options: {
        presets: [
          "@babel/preset-env",
          "@babel/preset-typescript",
          "babel-preset-typescript-vue",
        ],
        plugins: [
          ["@babel/plugin-proposal-decorators", { legacy: true }],
          ["@babel/plugin-proposal-class-properties", { loose: true }],
        ],
      },
    },
  },

  // Heavier settings only to build bokeh.
  {
    test: /(@bokeh\/).*\.js/,
    use: {
      loader: require.resolve("babel-loader"),
      options: {
        presets: ["@babel/preset-env"],
        plugins: [
          "@babel/plugin-proposal-export-namespace-from",
          ["@babel/plugin-transform-runtime", { regenerator: true }],
        ],
        sourceType: "unambiguous",
      },
    },
  },

  // Styling files rule
  {
    test: /\.(sa|sc|c)ss$/,
    use: [
      require.resolve("vue-style-loader"),
      MiniCssExtractPlugin.loader,
      {
        loader: require.resolve("css-loader"),
        options: { sourceMap: true },
      },
      {
        loader: require.resolve("postcss-loader"),
        options: {
          postcssOptions: {
            plugins: [require.resolve("autoprefixer")],
          },
        },
      },
      require.resolve("sass-loader"),
    ],
  },

  // Other file assets rule
  {
    test: /.(jpg|png|woff(2)?|eot|ttf|svg)$/,
    loader: require.resolve("file-loader"),
    options: {
      publicPath: "/static/",
    },
  },
];

const PLUGINS = [
  new CleanWebpackPlugin(),
  new VueLoaderPlugin(),
  new MiniCssExtractPlugin({
    // Options similar to the same options in webpackOptions.output
    // both options are optional
    filename: "[name]_[hash].css",
    chunkFilename: "[id].css",
  }),
  new ForkTsCheckerWebpackPlugin({
    typescript: {
      extensions: {
        vue: true,
      },
    },
  }),
  new BundleTracker({
    path: path.resolve(STATS_DIR),
    filename: "webpack-stats.json",
  }),
  new MomentLocalesPlugin({
    localesToKeep: ["pl"],
  }),
];

const WEBPACK_CONFIG = {
  entry: ASSET_DEFS,
  output: {
    path: path.resolve(BUNDLE_OUTPUT_DIR),
    filename: DEV_MODE ? "[name]_[hash].js" : "[name]_[hash].min.js",
  },
  module: {
    rules: RULES,
  },
  resolve: {
    plugins: [PnpWebpackPlugin],
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
  resolveLoader: {
    plugins: [PnpWebpackPlugin.moduleLoader(module)],
  },
  plugins: PLUGINS,
  mode: DEV_MODE ? "development" : "production",
  devtool: DEV_MODE ? "cheap-eval-source-map" : false,
  watchOptions: {
    poll: 2000,
  },
  stats: {
    children: false,
  },
};

module.exports = WEBPACK_CONFIG;
