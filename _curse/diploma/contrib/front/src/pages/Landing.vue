<template>
    <v-container class="login-form-wrapper" v-if="loginData.isVisible">
        <v-container class="login-form">
            <v-card class="mx-auto px-6 py-8" max-width="344">
                <v-form
                    v-model="loginData.form"
                    @submit.prevent="onSubmit"
                >
                    <h3>{{ loginData.isLogin ? 'Войти' : 'Зарегистрироваться' }}</h3>
                    <br>
                    <v-text-field
                        v-if="!loginData.isLogin"
                        v-model="loginData.name"
                        :readonly="loginData.isLoading"
                        :rules="[rules.required, rules.tooLong(20)]"
                        class="mb-2"
                        label="Имя"
                        clearable
                    ></v-text-field>

                    <v-text-field
                        v-model="loginData.email"
                        :readonly="loginData.isLoading"
                        :rules="[rules.required, rules.email, rules.tooLong(255)]"
                        class="mb-2"
                        label="Почта"
                        clearable
                    ></v-text-field>

                    <v-text-field
                        v-model="loginData.password"
                        :append-icon="loginData.showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                        :type="loginData.showPassword ? 'text' : 'password'"
                        :readonly="loginData.isLoading"
                        :rules="[rules.required]"
                        label="Пароль"
                        class="input-group--focused"
                        placeholder="Введите пароль"
                        clearable
                        @click:append="loginData.showPassword = !loginData.showPassword"
                    ></v-text-field>

                    <h4 v-if="loginData.displayError" style="color: red">{{ loginData.displayError }}</h4>

                    <v-btn
                        :disabled="!loginData.form"
                        :loading="loginData.isLoading"
                        color="success"
                        size="large"
                        type="submit"
                        variant="elevated"
                        block
                    >{{ loginData.isLogin ? 'Войти' : 'Зарегистрироваться' }}</v-btn>

                    <br>

                    <v-btn
                        @click="loginData.isVisible = false"
                        color="error"
                        size="large"
                        variant="elevated"
                        block
                    >Отмена</v-btn>

                    <br>

                    <v-btn
                        v-if="loginData.isLogin"
                        @click="onForgotPassword"
                        color="purple"
                        size="large"
                        variant="elevated"
                        block
                    >Забыли пароль?</v-btn>

                    <br>

                    <v-btn
                        v-if="loginData.isLogin"
                        @click="onConfirmEmail"
                        color="yellow"
                        size="large"
                        variant="elevated"
                        block
                    >Нужно подтвердить почту?</v-btn>

                    <v-container>
                        <v-row>
                            <a v-for="provider in oauthProviders" :href="`${Config.backend_address}/oauth/login/?provider=${provider.code}`">
                                <v-container>
                                    <v-row>
                                        <v-icon>{{provider.icon}}</v-icon>
                                    </v-row>
                                    <v-row>
                                        {{provider.name}}
                                    </v-row>
                                </v-container>
                            </a>
                        </v-row>
                    </v-container>
                </v-form>
            </v-card>
        </v-container>
    </v-container>
    <v-app>
        <v-app-bar color="primary" dark>
            <v-toolbar-title>{{ appName }}</v-toolbar-title>
            <v-spacer></v-spacer>
            <div v-if="userRole === Config.userRoles.guest" class="mr-4">
                <v-btn color="secondary" @click="() => {
                    loginData.isVisible = true;
                    loginData.isLogin = true;
                }" variant="outlined">Войти</v-btn>
                <v-btn color="secondary" @click="() => {
                    loginData.isVisible = true;
                    loginData.isLogin = false;
                }" variant="outlined" class="ml-4">Зарегистрироваться</v-btn>
            </div>
            <div v-else-if="userRole === Config.userRoles.user" class="mr-4">
                <router-link to="/articles">
                    <v-btn>Статьи</v-btn>
                </router-link>
            </div>
            <div v-else-if="userRole === Config.userRoles.mod" class="mr-4">
                <router-link to="/reports">
                    <v-btn>Жалобы</v-btn>
                </router-link>
            </div>
            <div v-else class="mr-4">
                <router-link to="/users">
                    <v-btn>Пользователи</v-btn>
                </router-link>
            </div>
            <div v-if="userRole !== Config.userRoles.guest" class="mr-4">
                <v-btn @click="logout">Выйти</v-btn>
            </div>
        </v-app-bar>

        <v-main>
            <v-container class="fill-height d-flex flex-column justify-center align-center">
                <v-row class="text-center">
                    <v-col cols="12">
                        <h1 class="text-h3 font-weight-bold mb-4">Welcome to {{ appName }}</h1>
                        <p class="text-body-1 mb-8">
                            This is a beautifully crafted landing page built with Vue.js 3 and Vuetify. 
                            Discover the amazing features and join our community today!
                        </p>
                    </v-col>
                </v-row>

                <v-row class="text-center">
                    <v-col cols="12" sm="4" v-for="(feature, index) in features" :key="index">
                        <v-card class="pa-4 mx-auto" elevation="2" max-width="350"> 
                            <v-icon :icon="feature.icon" size="large" color="primary"></v-icon>
                            <v-card-title class="text-h5 mt-2">{{ feature.title }}</v-card-title>
                            <v-card-text class="text-body-2">{{ feature.description }}</v-card-text>
                        </v-card>
                    </v-col>
                </v-row>
                <v-row class="mt-10"></v-row>
            </v-container>

            <v-footer color="primary" padless>
                <v-row justify="center" no-gutters>
                    <v-btn
                        v-for="icon in icons"
                        :key="icon"
                        class="mx-4 white--text"
                        icon
                    >
                        <v-icon size="24px">{{ icon }}</v-icon>
                    </v-btn>
                </v-row>
                <v-col class="text-center white--text">
                    {{ new Date().getFullYear() }} — <strong>{{ appName }}</strong>
                </v-col>
            </v-footer>

        </v-main>
    </v-app>
</template>


<script setup lang="ts">
import { ref, reactive } from 'vue'
import {fetch_data, fetchPersonalInfo, logout} from '../helpers';
import { Config, validationRules as rules } from '../settings';
import { UnnecessaryEventEmitter } from '../eventBus';

const loginData = reactive({
    form: false,
    displayError: '',
    isVisible: false,
    isLogin: true,
    isLoading: false,
    showPassword: false,
    email: '',
    password: '',
    name: '',
})
const userRole = ref(
    localStorage.getItem(Config.userInfoProperty) ? JSON.parse(localStorage.getItem(Config.userInfoProperty) as string).role : Config.userRoles.guest
);

const oauthProviders = [
    {
        code: 'google',
        name: 'Google',
        icon: 'google'
    },
    {
        code: 'mail_ru',
        name: 'Mail.ru',
        icon: 'at'
    },
    {
        code: 'yandex',
        name: 'Яндекс',
        icon: 'alpha-y-circle'
    },
    {
        code: 'vk',
        name: 'ВКонтакте',
        icon: 'alpha-v-box'
    }
]

const icons = ref([
    'mdi-facebook',
    'mdi-twitter',
    'mdi-linkedin',
    'mdi-instagram',
])
const appName = ref('GPTranslate')
const features = ref([
    { 
        icon: 'mdi-rocket-launch',
        title: 'Fast and Powerful',
        description: 'Experience lightning-fast performance and seamless navigation with our optimized platform.'
    },
    { 
        icon: 'mdi-shield-check',
        title: 'Secure and Reliable',
        description: 'Your data is safe with us. We employ industry-standard security measures to protect your information.'
    },
    { 
        icon: 'mdi-account-group', 
        title: 'Join Our Community',
        description: 'Connect with other users, share your experiences, and learn from each other in our vibrant community.'
    }
])

async function onSubmit() {
    loginData.isLoading = true;
    try {
        const result = await fetch_data(
            `${Config.backend_address}/auth/${loginData.isLogin ? 'login' : 'register'}/`,
            'POST',
            JSON.stringify({
                email: loginData.email,
                password: loginData.password,
                name: loginData.name
            }),
            false,
            true
        )
        console.log(result)
        if (result) {
            loginData.isVisible = false;
            loginData.form = false;
            loginData.email = '';
            loginData.password = '';
            loginData.name = '';
            loginData.showPassword = false;

            if (!loginData.isLogin) return;

            await fetchPersonalInfo()
            location.reload()

            UnnecessaryEventEmitter.emit('AlertMessage', {
                title: result.detail,
                text: undefined,
                severity: 'info'
            })
        }
    } catch(e) {
        loginData.displayError = e as string;
        setTimeout(function() {
            loginData.displayError = '';
        }, 3000)
    }
    loginData.isLoading = false;
}

async function onForgotPassword() {
    if (!loginData.email) {
        loginData.displayError = 'Введите почту';
        return
    }
    const response = await fetch_data(
        `${Config.backend_address}/auth/restore-password/request/?email=${loginData.email}`,
        'POST',
    )
    if (response) {
        UnnecessaryEventEmitter.emit('AlertMessage', {
            title: response.message,
            text: undefined,
            severity: 'info'
        })
        loginData.isVisible = false;
    }
}

async function onConfirmEmail() {
    if (!loginData.email) {
        loginData.displayError = 'Введите почту';
        return
    }
    const response = await fetch_data(
        `${Config.backend_address}/auth/confirm-email/request/?email=${loginData.email}`,
        'POST',
    )
    if (response) {
        UnnecessaryEventEmitter.emit('AlertMessage', {
            title: response.message,
            text: undefined,
            severity: 'info'
        })
        loginData.isVisible = false;
    }
}
</script>

<style scoped>
.fill-height {
  min-height: calc(100vh - 64px);
}

.login-form {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    max-width: 90%;
    border-radius: 8px;
}

.login-form-wrapper {
    z-index: 9998;
    margin: 0;
    padding: 0;
    position: fixed;
    width: 100vw;
    max-width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
}
</style>