import Vue from 'vue';
import VueRouter from 'vue-router';

Vue.use(VueRouter);

export const router = new VueRouter({
  mode: 'history',
  routes: [
    {
      path: '/',
      component: () =>
        import(/* webpackChunkName: 'todos-page' */ '@/views/DCPlatform'),
    },
  ],
});
