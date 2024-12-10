module.exports = {
    preset: "ts-jest",
    testEnvironment: "jsdom",
    transform: {
      "^.+\\.vue$": "vue-jest",
      "^.+\\.(js|jsx|ts|tsx)$": "babel-jest",
    },
    moduleFileExtensions: ["js", "json", "jsx", "ts", "tsx", "vue"],
};