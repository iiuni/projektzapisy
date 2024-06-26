module.exports = {
  parser: "vue-eslint-parser",
  parserOptions: {
    tsconfigRootDir: __dirname,
    project: ["./tsconfig.json"],
    extraFileExtensions: [".vue"],
    parser: "@typescript-eslint/parser",
    sourceType: "module",
  },
  extends: [
    // generic rulesets
    "eslint:recommended",
    "plugin:vue/recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking",
  ],
  rules: {
    "vue/component-tags-order": [
      "error",
      {
        order: ["script", "template", "style"],
      },
    ],

    // some rules could be enabled once the code quality is improved
    // for more details check https://eslint.vuejs.org/rules/
    // and https://typescript-eslint.io/rules/

    // essential vue rules:
    "vue/require-valid-default-prop": "off",
    "vue/require-v-for-key": "off",
    // strongly-recommended vue rules:
    "vue/singleline-html-element-content-newline": "off",
    "vue/html-closing-bracket-newline": "off",
    "vue/max-attributes-per-line": "off",
    "vue/attribute-hyphenation": "off",
    "vue/require-default-prop": "off",
    "vue/html-self-closing": "off",
    "vue/prop-name-casing": "off",
    "vue/v-bind-style": "off",
    "vue/html-indent": "off",
    "vue/v-on-style": "off",
    // recommended vue rules:
    "vue/order-in-components": "off",
    "vue/attributes-order": "off",
    "vue/this-in-template": "off",
    "vue/no-v-html": "off",

    // recommended typescript rules
    // errors:
    "@typescript-eslint/no-array-constructor": "off",
    "@typescript-eslint/no-inferrable-types": "off",
    "@typescript-eslint/no-this-alias": "off",
    "@typescript-eslint/ban-types": "off",
    // warnings:
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-non-null-assertion": "off",
    "@typescript-eslint/no-explicit-any": "off",
    "@typescript-eslint/no-unused-vars": "off",
    // recommended-requiring-type-checking typescript rules
    // errors:
    "@typescript-eslint/no-unsafe-member-access": "off",
    "@typescript-eslint/restrict-plus-operands": "off",
    "@typescript-eslint/no-unsafe-assignment": "off",
    "@typescript-eslint/no-floating-promises": "off",
    "@typescript-eslint/no-misused-promises": "off",
    "@typescript-eslint/no-unsafe-return": "off",
    "@typescript-eslint/no-unsafe-call": "off",
    "@typescript-eslint/unbound-method": "off",
    "@typescript-eslint/require-await": "off",
  },
};
