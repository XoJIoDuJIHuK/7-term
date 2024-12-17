import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import LandingPage from './pages/Landing.vue'
// @ts-ignore
import ErrorPage from './pages/Error.vue'
import articles_router from './pages/articles/router'
import configs_router from './pages/configs/router'
import reports_router from './pages/reports/router'

// @ts-ignore
import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

import 'material-design-icons-iconfont/dist/material-design-icons.css'
import BaseLayout from './components/BaseLayout.vue'
import SessionsPage from './pages/Sessions.vue'
import { Config } from './settings'
import ReportList from './pages/ReportList.vue'
import UserList from './pages/UserList.vue'
import PromptList from './pages/PromptList.vue'
import ModelList from './pages/ModelList.vue'
import AnalyticsPage from "./pages/Analytics.vue";
import OAuthCallback from "./pages/OAuthCallback.vue";
import ChangePersonalInfo from './pages/ChangePersonalInfo.vue'
import ConfirmPasswordChange from "./pages/ConfirmPasswordChange.vue";
// @ts-ignore
import ConfirmEmail from "./pages/ConfirmEmail.vue";

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
                { path: 'sessions', component: SessionsPage},
                { path: 'users', component: UserList },
                { path: 'prompts', component: PromptList },
                { path: 'models', component: ModelList },
                { path: 'reports', component: ReportList },
                { path: 'sessions', component: SessionsPage },
                { path: 'personal', component: ChangePersonalInfo },
                // { path: 'analytics', component: AnalyticsPage },
                { path: 'analytics', component: AnalyticsPage },
            ],
            props: true
        },
        { path: '/landing', component: LandingPage },
        { path: '/error', name: 'ErrorPageChild', component: ErrorPage},
        { path: '/oauth/:provider/oauth-callback', name:'OAuth callback', component: OAuthCallback },
        { path: '/change-password', name: 'Change Password', component: ConfirmPasswordChange },
        { path: '/confirm-email', name: 'Confirm Email', component: ConfirmEmail },
        articles_router,
        configs_router,
        reports_router,
    ]
})

// @ts-ignore
router.beforeEach((to, from, next) => {
    function anyStartsWith(substr: string, arr: Array<string>) {
        for (let s of arr) {
            if (substr.startsWith(s)) {
                return true;
            }
        }
        return false;
    }
    function modPathMatch(path: string) {
        if (anyStartsWith(path, ['/reports', '/sessions', '/me', '/personal'])) return true;
        const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
        const match = path.match(/^\/articles\/([0-9a-f-]+)\/report\/$/i);

        if (match) {
            const articleId = match[1];
            return uuidRegex.test(articleId);
        }
    }

    const path = to.path
    if (
        ['/', '/landing', '/error', '/change-password', '/confirm-email'].includes(path)
        || path.includes('oauth-callback')
    ) {
        next()
        return
    }
    const cachedUserInfo = localStorage.getItem(Config.userInfoProperty);
    if (!cachedUserInfo) {
        console.error('Not found cached user info')
        next({ path: '/' })
        return
    }
    const role = JSON.parse(cachedUserInfo as string).role;
    if ((
        role == Config.userRoles.user && !anyStartsWith(path, ['/articles', '/configs', '/reports', '/sessions', '/me', '/personal'])
        ) || (
        role == Config.userRoles.mod && !modPathMatch(path)
        ) || (
        role == Config.userRoles.admin && !anyStartsWith(path, ['/users', '/prompts', '/models', '/analytics', '/sessions', '/me', '/personal'])
        )
    ) {
        console.error(`403 yopta: ${role} ${path}`)
        next({ path: '/error' })
        return
    }
    next()
    return
})


createApp(App).use(vuetify).use(router).mount('#app')
