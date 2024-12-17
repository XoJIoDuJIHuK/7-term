<template>
    <v-text-field v-model="enteredName"></v-text-field>
    <v-btn @click="updateName">Обновить имя</v-btn>
</template>

<script setup lang="ts">
import {fetch_data} from "../helpers.ts";
import { ref } from "vue";
import {Config} from "../settings.ts";

const userData = JSON.parse(localStorage.getItem(Config.userInfoProperty) as string)
const enteredName = ref(userData.name)

async function updateName() {
    if (enteredName.value !== '') {
        const response = await fetch_data(
            `${Config.backend_address}/users/${userData.id}/name/`,
            'PATCH',
            JSON.stringify({
                name: enteredName.value
            })
        )
        if (!response) return
        userData.name = enteredName.value
        localStorage.setItem(Config.userInfoProperty, JSON.stringify(userData))
        location.reload()
    }
}
</script>