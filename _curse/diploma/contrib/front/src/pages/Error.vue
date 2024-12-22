<template>
    <v-container class="error-container">
        <v-row><h1>404</h1></v-row>
        <v-row><h2>Страница не найдена</h2></v-row>
        <v-row>
            <v-col><v-btn color="green" @click="router.push('/')">На главную</v-btn></v-col>
            <v-col><v-btn color="red" @click="logout">Выйти из учётной записи</v-btn></v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { useRouter } from "vue-router";
import { logout } from '../helpers';

const router = useRouter();
</script>

<style scoped>
.error-container {
    position: absolute;
    display: flex;
    flex-direction: column;
    left: 12vw;
    width: 100vw;
    height: 50%;
    top: 20%;
}
.v-row {
    justify-content: center;
}
.v-col {
    width: fit-content;
    max-width: max-content;
}
</style>