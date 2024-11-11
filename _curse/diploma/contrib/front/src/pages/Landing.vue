<template>
    <v-container v-if="loginData.isVisible">
        <v-card class="mx-auto px-6 py-8" max-width="344">
            <v-form
                v-model="loginData.form"
                @submit.prevent="onSubmit"
            >
                <h3>{{ loginData.isLogin ? 'Login' : 'Register' }}</h3>
                <br>
                <v-text-field
                    v-if="!loginData.isLogin"
                    v-model="loginData.name"
                    :readonly="loginData.isLoading"
                    :rules="[required]"
                    class="mb-2"
                    label="Name"
                    clearable
                ></v-text-field>

                <v-text-field
                    v-model="loginData.email"
                    :readonly="loginData.isLoading"
                    :rules="[required]"
                    class="mb-2"
                    label="Email"
                    clearable
                ></v-text-field>

                <v-text-field
                    v-model="loginData.password"
                    :readonly="loginData.isLoading"
                    :rules="[required]"
                    label="Password"
                    placeholder="Enter your password"
                    clearable
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
                >Sign {{ loginData.isLogin ? 'In' : 'Up' }}</v-btn>

                <br>

                <v-btn
                    @click="loginData.isVisible = false"
                    color="error"
                    size="large"
                    variant="elevated"
                    block
                >Cancel</v-btn>

                <v-btn
                    v-if="loginData.isLogin"
                    @click="onForgotPassword"
                    color="purple"
                    size="large"
                    variant="elevated"
                    block
                >Forgot password</v-btn>
            </v-form>
        </v-card>
    </v-container>
    <v-app>
        <v-app-bar color="primary" dark>
            <v-toolbar-title>{{ appName }}</v-toolbar-title>
            <v-spacer></v-spacer>
            <div v-if="userRole === Config.userRoles.guest" class="mr-4">
                <v-btn color="secondary" @click="() => {
                    loginData.isVisible = true;
                    loginData.isLogin = true;
                }" variant="outlined">Login</v-btn>
                <v-btn color="secondary" @click="() => {
                    loginData.isVisible = true;
                    loginData.isLogin = false;
                }" variant="outlined" class="ml-4">Register</v-btn>
            </div>
            <div v-else-if="userRole === Config.userRoles.user" class="mr-4">
                <router-link to="/articles">
                    <v-btn>Articles</v-btn>
                </router-link>
            </div>
            <div v-else-if="userRole === Config.userRoles.mod" class="mr-4">
                <router-link to="/reports">
                    <v-btn>Reports</v-btn>
                </router-link>
            </div>
            <div v-else class="mr-4">
                <router-link to="/users">
                    <v-btn>Users</v-btn>
                </router-link>
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
import { fetch_data, logout } from '../helpers';
import { Config } from '../settings';
import { UnnecessaryEventEmitter } from '../eventBus';

const loginData = reactive({
    form: false,
    displayError: '',
    isVisible: false,
    isLogin: true,
    isLoading: false,
    email: '',
    password: '',
    name: '',
})
const userRole = ref(
    localStorage.getItem(Config.userInfoProperty) ? JSON.parse(localStorage.getItem(Config.userInfoProperty) as string).role : Config.userRoles.guest
);

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

function required (v: string) {
    return !!v || 'Field is required'
}

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
        if (result) {
            loginData.isVisible = false;
            loginData.form = false;
            loginData.email = '';
            loginData.password = '';
            loginData.name = '';
            const userInfoResponse = await fetch_data(`${Config.backend_address}/users/me/`)
            if (!userInfoResponse) {
                await logout()
                return
            }
            localStorage.setItem(Config.userInfoProperty, JSON.stringify(userInfoResponse.data.user));
            userRole.value = userInfoResponse.data.user.role;

            UnnecessaryEventEmitter.emit('AlertMessage', {
                title: result.detail,
                text: undefined,
                severity: 'info'
            })
        }
    } catch(e) {
        console.log(e)
        loginData.displayError = e as string;
        setTimeout(function() {
            loginData.displayError = '';
        }, 3000)
    }
    loginData.isLoading = false;
}

async function onForgotPassword() {
    if (!loginData.email) {
        loginData.displayError = 'Email is required';
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
</script>

<style scoped>
.fill-height {
  min-height: calc(100vh - 64px);
}


</style>