const path = require("path");

const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const EventHooksPlugin = require("event-hooks-webpack-plugin");
const BundleTracker = require("webpack-bundle-tracker");

const nucleusConfig = require("./resources/webpack/nucleus.js");
const developmentConfig = require("./resources/webpack/development.js");
const productionConfig = require("./resources/webpack/production.js");

const buildPath = path.resolve(__dirname, "resources", "static", "wp");

module.exports = (env, argv) => {
  const development = argv.mode === "development";

  const config = {
    devtool: "source-map",
    entry: {
      main: ["./resources/src/index.js"],
      review: ["./resources/src/js/components/review.js"],
      prevent_enter_keydown_Event: [
        "./resources/src/preventEnterKeydownEvent.js"
      ],
      collection_groups_edit_page_form: [
        "./resources/src/js/components/collectionsGroupsEditPageForm.js"
      ],
      collection_groups_detail_page_form: [
        "./resources/src/js/components/collectionsGroupsDetailPageForm.js"
      ],
      collection_groups_card_component_form: [
        "./resources/src/js/components/collectionsGroupsCardComponentForm.js"
      ],
      collections_add_to_groups_api: [
        "./resources/src/js/fetch_api_calls/collections_add_to_groups.js"
      ],
      collections_group_favorites_api: [
        "./resources/src/js/fetch_api_calls/collections_add_to_remove_from_favorites_group.js"
      ],
      content_resource_collections_edit_iframe_load_events: [
        "./resources/src/js/components/content_resource_collections_edit_iframe/load_iframe_events.js"
      ],
      content_resource_collections_edit_iframe_search_select_component: [
        "./resources/src/js/components/content_resource_collections_edit_iframe/search_select_component.js"
      ],
      ignore_shared_resource_api: [
        "./resources/src/js/fetch_api_calls/ignore_shared_resource.js"
      ],
      inviteCollaborators: ["./resources/src/inviteCollaborators.js"],
      shareResource: ["./resources/src/js/components/shareResource.js"],
      search: ["./resources/src/search.js"],
      theme_primary_color: ["./resources/src/theme_primary_color.js"],
      theme_secondary_color: ["./resources/src/theme_secondary_color.js"],
      expositions: ["./resources/src/expositions.js"],
      style_guide: ["./resources/src/style_guide.js"]
    },
    output: {
      filename: development ? "[name].js" : "[name].[hash:20].js",
      path: buildPath
    },
    node: {
      fs: "empty"
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          loader: "babel-loader",
          options: {
            presets: [
              [
                "@babel/preset-env",
                {
                  useBuiltIns: "entry",
                  corejs: { version: 3.6 }
                }
              ]
            ]
          },
          rules: [
            {
              exclude: /resources\/src\/js\/vendor/,
              loader: "eslint-loader"
            }
          ]
        },
        {
          test: /\.(s?css)$/,
          use: [
            development
              ? {
                  // creates style nodes from JS strings
                  loader: "style-loader"
                }
              : {
                  loader: MiniCssExtractPlugin.loader
                },
            {
              // translates CSS into CommonJS
              loader: "css-loader",
              options: {
                sourceMap: true
              }
            },
            {
              // Runs compiled CSS through postcss for vendor prefixing
              loader: "postcss-loader",
              options: {
                sourceMap: true
              }
            },
            {
              // compiles Sass to CSS
              loader: "sass-loader",
              options: {
                sassOptions: {
                  outputStyle: "expanded"
                },
                sourceMap: true
              }
            }
          ]
        },
        {
          // Load all images as base64 encoding if they are smaller than 8192 bytes
          test: /\.(png|jpg|gif)$/,
          use: [
            {
              loader: "url-loader",
              options: {
                name: development
                  ? "[path][name].[ext]"
                  : "[name].[hash:20].[ext]",
                limit: 1
              }
            }
          ]
        },
        {
          test: /\.(woff2?|ttf|otf|eot|svg)$/,
          use: [
            {
              loader: "file-loader",
              options: {
                name: development
                  ? "[path][name].[ext]"
                  : "[name].[hash:20].[ext]"
              }
            }
          ]
        }
      ]
    },
    plugins: [
      new EventHooksPlugin({
        done: nucleusConfig
      }),
      new CleanWebpackPlugin(),
      new BundleTracker({
        filename: "./webpack-stats.json"
      })
    ],
    watchOptions: {
      poll: true
    }
  };

  development ? developmentConfig(config) : productionConfig(config);

  return config;
};
