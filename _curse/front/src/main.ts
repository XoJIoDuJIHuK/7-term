// src/main.js
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import LandingPage from './components/LandingPage.vue'
import LoginPage from './components/LoginPage.vue'
import RegisterPage from './components/RegisterPage.vue'
import Dashboard from './components/Dashboard.vue' // Example protected page
import BaseLayout from './components/BaseLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: LandingPage },
    { path: '/login', component: LoginPage },
    { path: '/register', component: RegisterPage },
    {
      path: '/dashboard', // Example protected route
      component: BaseLayout,
      children: [
        { path: '', component: Dashboard } 
      ]
    }
  ]
})

createApp(App).use(router).mount('#app')
