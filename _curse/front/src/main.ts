// src/main.js
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import LandingPage from './components/LandingPage.vue'
import LoginPage from './components/LoginPage.vue'
import RegisterPage from './components/RegisterPage.vue'
import Dashboard from './components/Dashboard.vue' // Example protected page
import BaseLayout from './components/BaseLayout.vue'
import ArticlesList from './components/ArticlesList.vue'

import 'vuetify/styles'; // Import Vuetify styles
import { createVuetify } from 'vuetify'; // Import Vuetify creation function
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import ArticlesPage from './components/ArticlesPage.vue'
import EditArticlePage from './components/EditArticlePage.vue'

const vuetify = createVuetify({
  components,
  directives,
});

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: LandingPage },
    { path: '/login', component: LoginPage },
    { path: '/register', component: RegisterPage },
    {
      path: '/articles/',
      component: BaseLayout,
      children: [
        { path: '', component: ArticlesPage },
        { path: 'create/', component: EditArticlePage },
        // { path: ':article_id/', component: EditArticlePage, props: true },
      ]
    },
    {
      path: '/dashboard/', // Example protected route
      component: BaseLayout,
      children: [
        { path: '', component: Dashboard } 
      ]
    }
  ]
})

createApp(App).use(vuetify).use(router).mount('#app')
