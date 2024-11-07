<template>
    <v-menu location="end">
        <template v-slot:activator="{ props }">
            <v-btn
                color="primary"
                dark
                v-bind="props"
            >
                {{ userInfo.name }}
            </v-btn>
        </template>

        <v-list>
            <v-list-item>
                <router-link to="/sessions">
                    <v-btn variant="tonal" color="primary">
                        <v-list-item-title>Sessions</v-list-item-title>
                    </v-btn>
                </router-link>
            </v-list-item>
            <v-list-item>
                <v-btn variant="tonal" color="primary" @click="logout">
                    <v-list-item-title>Logout</v-list-item-title>
                </v-btn>
            </v-list-item>
        </v-list>
    </v-menu>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { logout } from '../helpers';

const router = useRouter();

const userInfo = reactive({
    id: '',
    name: '',
    email: '',
    role: '',
})

onMounted(async () => {
    const cachedUserInfo = localStorage.getItem('userInfo') ? JSON.parse(localStorage.getItem('userInfo') as string) : {};
    if (!userInfo) {
        await logout(router);
    }
    userInfo.id = cachedUserInfo.id;
    userInfo.name = cachedUserInfo.name;
    userInfo.email = cachedUserInfo.email;
    userInfo.role = cachedUserInfo.role;
})


</script>