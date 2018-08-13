/* eslint-disable */
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import axios from 'axios'
import iView from 'iview'
import 'iview/dist/styles/iview.css'
import locale from 'iview/dist/locale/en-US';

import App from './App'
import router from './router'
import store from './store'

if (!process.env.IS_WEB) Vue.use(require('vue-electron'))
Vue.use(VueI18n)
Vue.use(iView, {locale})
Vue.http = Vue.prototype.$http = axios
Vue.config.productionTip = false

const i18n = new VueI18n({
    locale: 'en', // 语言标识
    messages: {
        'zh': require('./assets/lang/zh'),
        'en': require('./assets/lang/en')
    }
})

/* eslint-disable no-new */
new Vue({
  components: { App },
  i18n,
  router,
  store,
  template: '<App/>',
  mounted () {
    setInterval(() => {
      this.$store.dispatch('GET_DATA')
    }, 5000)
  }
}).$mount('#app')
