const path = require('path');

module.exports = {
    entry: './src/app',
    output: {
      path: path.resolve(__dirname, "dist"), // string
      filename: 'bundle.js'
    },
    module: {
      rules: [
        {
          test: /\.jsx?$/,
          exclude: /node_modules/,
          loader: 'babel-loader',
          options: { presets: [ '@babel/preset-env', '@babel/preset-react' ] }
        }
      ]
    },
    devServer: {
      contentBase: path.resolve(__dirname, "public"),
      proxy: {
        '/api': 'http://localhost:5000'
      }
    }
  };