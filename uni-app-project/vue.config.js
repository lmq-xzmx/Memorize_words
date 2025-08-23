const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: [],
  configureWebpack: {
    resolve: {
      fallback: {
        "path": require.resolve("path-browserify"),
        "os": require.resolve("os-browserify/browser"),
        "crypto": require.resolve("crypto-browserify")
      }
    }
  },
  chainWebpack: config => {
    // 确保webpack配置正确
    config.resolve.alias
      .set('@', require('path').resolve(__dirname, 'src'))
  }
})