const path = require('path');

module.exports = {
  entry: './app/my.ts',
  output: {
    filename: 'hrmeter.js',
    path: path.resolve(__dirname, 'static')
  }
};