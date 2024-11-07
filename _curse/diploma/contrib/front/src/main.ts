import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import LandingPage from './pages/Landing.vue'
import ErrorPage from './pages/Error.vue'
import articles_router from './pages/articles/router'
import configs_router from './pages/configs/router'
import reports_router from './pages/reports/router'

import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

import 'material-design-icons-iconfont/dist/material-design-icons.css'
import BaseLayout from './components/BaseLayout.vue'
import SessionsPage from './pages/Sessions.vue'

const vuetify = createVuetify({
    components,
    directives,
});

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', redirect: '/landing' },
        {
            path: '/',
            component: BaseLayout,
            children: [
                { path: 'error', name: 'ErrorPageChild', component: ErrorPage},
                { path: 'sessions', component: SessionsPage},
            ],
            props: true
        },
        { path: '/landing', component: LandingPage },
        { path: '/sessions', component: SessionsPage },
        articles_router,
        configs_router,
        reports_router,
    ]
})


createApp(App).use(vuetify).use(router).mount('#app')
