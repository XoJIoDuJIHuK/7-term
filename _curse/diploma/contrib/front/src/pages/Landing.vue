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
                        :rules="[rules.required, rules.maxLength(20)]"
                        class="mb-2"
                        label="Имя"
                        clearable
                    ></v-text-field>

                    <v-text-field
                        v-model="loginData.email"
                        :readonly="loginData.isLoading"
                        :rules="[rules.required, rules.email, rules.maxLength(255)]"
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

                    <br v-if="loginData.isLogin">

                    <v-btn
                        v-if="loginData.isLogin"
                        @click="onForgotPassword"
                        color="purple"
                        size="large"
                        variant="elevated"
                        block
                    >Забыли пароль?</v-btn>

                    <br v-if="loginData.isLogin">

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
                <v-btn color="blue" @click="() => {
                    loginData.isVisible = true;
                    loginData.isLogin = true;
                }" variant="elevated">Вход</v-btn>
                <v-btn color="blue" @click="() => {
                    loginData.isVisible = true;
                    loginData.isLogin = false;
                }" variant="elevated" class="ml-4">Регистрация</v-btn>
            </div>
            <div v-else-if="userRole === Config.userRoles.user" class="mr-4">
                <router-link to="/articles">
                    <v-btn variant="elevated" color="blue">Статьи</v-btn>
                </router-link>
            </div>
            <div v-else-if="userRole === Config.userRoles.mod" class="mr-4">
                <router-link to="/reports">
                    <v-btn variant="elevated" color="blue">Жалобы</v-btn>
                </router-link>
            </div>
            <div v-else class="mr-4">
                <router-link to="/users">
                    <v-btn variant="elevated" color="blue">Пользователи</v-btn>
                </router-link>
            </div>
            <div v-if="userRole !== Config.userRoles.guest" class="mr-4">
                <v-btn @click="logout">Выход</v-btn>
            </div>
        </v-app-bar>

        <v-main class="gradient-background">
            <v-container class="fill-height d-flex flex-column justify-center align-center">
                <v-row class="text-center">
                    <v-col cols="12">
                        <h1 class="text-h3 font-weight-bold mb-4">Добро пожаловать в {{ appName }}</h1>
                        <p class="text-body-1 mb-8">
                            Превосходный инструмент для перевода текстов любой сложности.<br>
                            Начните пользоваться уже сегодня!
                        </p>
                    </v-col>
                </v-row>

                <v-row class="text-center">
                    <v-col cols="12" sm="4" v-for="(feature, index) in features" :key="index">
                        <v-card class="pa-4 mx-auto" elevation="2" max-width="350">
                            <v-container class="flex flex-row justify-center h-auto">
                                <v-icon :icon="feature.icon" size="x-large" color="primary"></v-icon>
                            </v-container>
                            <v-card-title class="text-h5 mt-2">{{ feature.title }}</v-card-title>
                            <v-card-text class="text-body-2">{{ feature.description }}</v-card-text>
                        </v-card>
                    </v-col>
                </v-row>

                <v-row class="mt-10">
                    <v-col cols="12">
                        <h2 class="text-h5 font-weight-bold mb-4">Наша статистика</h2>
                        <v-card>
                            <v-card-text>
                                <canvas id="translationChart"></canvas>
                            </v-card-text>
                        </v-card>
                    </v-col>
                </v-row>
            </v-container>

            <v-footer color="primary" padless>
                <v-row justify="center" no-gutters>
                    <a :href="icon.href" v-for="icon in icons">
                        <v-btn
                            :key="icon.value"
                            class="mx-4 white--text"
                            icon
                        >
                            <v-icon size="30px" style="margin-top: 8px">{{ icon.value }}</v-icon>
                        </v-btn>
                    </a>
                </v-row>
                <v-col class="text-center white--text">
                    {{ new Date().getFullYear() }} — <strong>{{ appName }}</strong>
                </v-col>
            </v-footer>

        </v-main>
    </v-app>
</template>


<script setup lang="ts">
import {ref, reactive, onMounted} from 'vue'
import {fetch_data, fetchPersonalInfo, logout} from '../helpers';
import { Config, validationRules as rules } from '../settings';
import { UnnecessaryEventEmitter } from '../eventBus';
import { Chart, registerables } from 'chart.js';

const loginData = reactive({
    form: false,
    displayError: '',
    isVisible: false,
    isLogin: true,
    isLoading: false,
    showPassword: false,
    email: 'admin@d.com',
    password: 'string',
    name: '',
})
const userRole = ref(Config.userRoles.guest);

const oauthProviders = [
    {
        code: 'google',
        name: 'Google',
        icon: 'google'
    },
]

const icons = ref([
    { href: 'https://www.linkedin.com/in/aleh-t-30580927b/', value: 'mdi-linkedin' },
    { href: 'https://t.me/XoJIoDuJIHuK', value: 'mdi-telegram' },
    { href: 'https://vk.com/jertva_rastishki', value: 'mdi-vk' },
    { href: 'http://github.com/XoJIoDuJIHuK', value: 'mdi-github' },
])
const appName = ref('GPTranslate')
const features = ref([
    { icon: 'mdi-translate', title: 'Поражающая воображение скорость', description: 'Переводите множество документов большого объёма в сжатые сроки' },
    { icon: 'mdi-chart-line', title: 'Большой выбор моделей для перевода', description: 'Мы предлагаем прозрачный выбор инструментов, которыми вы пользуетесь' },
    { icon: 'mdi-account', title: 'Сохранение настроек', description: 'Нужно часто переводить похожие тексты на одни и те же языки? Сохраните настройку и пользуйтесь ей' },
]);

onMounted(async () => {
    const ctx = document.getElementById('translationChart');
    Chart.register(...registerables);
    //@ts-ignore
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Английский', 'Французский', 'Русский', 'Немецкий', 'Китайский'],
            datasets: [{
                label: 'Количество переводов',
                data: [120, 90, 60, 30, 50],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)',
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    if (await fetchPersonalInfo(false)) {
        userRole.value = localStorage.getItem(Config.userInfoProperty) ? JSON.parse(localStorage.getItem(Config.userInfoProperty) as string).role : Config.userRoles.guest;
    }
});

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

            UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
                title: result.detail,
                text: undefined,
                severity: 'info'
            })

            location.reload()
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
        UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
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
        UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
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

.feature-card {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    align-items: center;
}

.v-card {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
}

.v-icon {
    margin-bottom: 16px;
}

.v-card-title {
    margin-bottom: auto;
    text-align: center;
    text-wrap: wrap;
}

.v-card-text {
    margin-top: auto;
    text-align: center;
}

.gradient-background {
    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
    color: white;
}
</style>