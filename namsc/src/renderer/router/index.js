/* eslint-disable */
import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

export default new Router({
    routes: [
        {
            path: '/',
            name: 'landing-page',
            component: require('@/components/LandingPage').default,
            children: [
                {
                    path: '/issues',
                    name: 'issues',
                    component: require('@/components/Issues').default
                },
                {
                    path: '/settings',
                    name: 'settings',
                    component: require('@/components/Settings').default
                }
            ]
        },
        {
            path: '*',
            redirect: '/'
        }
    ]
})
