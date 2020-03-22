// JavaScript modules
require('@fortawesome/fontawesome-free/js/all');
const $ = require('jquery');
require('popper.js');
require('bootstrap');
// require('datatables.net');
require('datatables.net-bs4');

require.context(
  '../img', // context folder
  true, // include subdirectories
  /.*/, // RegExp
);

// Your own code
require('./plugins.js');
require('./script.js');
