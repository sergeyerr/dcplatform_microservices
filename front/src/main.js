import Vue from 'vue';
import App from './App.vue';
import { router } from '@/router';
import 'vue-prism-editor/dist/prismeditor.min.css';
require('../node_modules/prismjs/themes/prism.css');

Vue.config.productionTip = false;

import { PrismEditor } from 'vue-prism-editor';
// eslint-disable-next-line no-unused-vars
window.onerror = function(message, source, line, column, error) {
  console.log('Error occured:', message);
};

Vue.config.errorHandler = function(err, vm, info) {
  console.log(`Error: ${err.toString()}\nInfo: ${info}`);
};

Vue.component('PrismEditor', PrismEditor);

new Vue({
  router,
  render: h => h(App),
}).$mount('#app');
