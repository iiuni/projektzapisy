"use strict";
const path = require("path");

const PnpWebpackPlugin = require("pnp-webpack-plugin");

const BundleTracker = require("webpack-bundle-tracker");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const ForkTsCheckerWebpackPlugin = require("fork-ts-checker-webpack-plugin");
const VueLoaderPlugin = require("vue-loader/lib/plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const TerserPlugin = require("terser-webpack-plugin");

const DEV_MODE = process.env.NODE_ENV !== "production";

const BUNDLE_OUTPUT_DIR = "compiled_assets";
const ASSET_DEF_SEARCH_DIR = "apps";
const STATS_DIR = "webpack_resources";

const ASSET_DEFS = require(path.resolve("webpack_resources/asset-defs.js"));

// List containing all rules needed to compile all types of
// assets used in PZ. If needed, new rules can be easily appended
// to the end of this list.
const RULES = [
  {
    test: /\.vue$/,
    use: require.resolve("vue-loader"),
    exclude: /node_modules/,
  },

  // Typescript is only stripped-down to JS, not type-checked.
  {
    test: /\.ts$/,
    use: {
      loader: require.resolve("ts-loader"),
      options: { transpileOnly: true, appendTsSuffixTo: [/\.vue$/] },
    },
  },

  // Bokeh needs to be translated by babel because it is compiled in a way that
  // webpack is not able to understand.
  {
    test: /(@bokeh\/).*\.js$/,
    use: {
      loader: require.resolve("babel-loader"),
      options: {
        presets: [
          [
            "@babel/preset-env",
            { bugfixes: true, targets: { esmodules: true } },
          ],
        ],
      },
    },
  },

  // Styles are compiled, post-processed (vendor-prefixes) and extracted to
  // separate css files.
  {
    test: /\.(sa|sc|c)ss$/,
    use: [
      MiniCssExtractPlugin.loader,
      require.resolve("css-loader"),
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

  // Other files are copied raw.
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
    filename: "[name]_[hash].css",
    chunkFilename: "[id].css",
  }),
  // Do type-checking in parallel, but only run it in tests.
  process.env.NODE_ENV === "test"
    ? new ForkTsCheckerWebpackPlugin({
        typescript: {
          extensions: {
            vue: true,
          },
        },
      })
    : false,
  new BundleTracker({
    path: path.resolve(STATS_DIR),
    filename: "webpack-stats.json",
  }),
].filter(Boolean);

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
      moment$: "dayjs",
      lodash$: "lodash-es",
      "@": path.resolve(ASSET_DEF_SEARCH_DIR),
    },
  },
  resolveLoader: {
    plugins: [PnpWebpackPlugin.moduleLoader(module)],
  },
  plugins: PLUGINS,
  mode: DEV_MODE ? "development" : "production",
  devtool: DEV_MODE ? "eval-cheap-source-map" : false,
  watchOptions: {
    poll: 2000,
  },
  stats: {
    assets: false,
    children: false,
  },
  optimization: {
    minimizer: [
      // Skip part of minimization that takes the most time (compressing
      // whitespace).
      new TerserPlugin({
        terserOptions: {
          ecma: 8,
          comments: false,
          compress: false,
        },
      }),
    ],
  },
};

module.exports = WEBPACK_CONFIG;
