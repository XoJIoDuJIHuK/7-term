<template>
    <v-btn
        @click="closeSessions"
        variant="elevated"
        color="red"
    >
        Close all
    </v-btn>
    <v-list lines="one">
        <v-list-item
            v-for="session in sessions"
            :key="session.id"
            :title="session.ip"
            :subtitle="(new Date(session.created_at)).toLocaleString()"
        ></v-list-item>
    </v-list>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { fetch_data, logout } from '../helpers';
import { Config } from '../settings';
import { UnnecessaryEventEmitter } from '../eventBus';

const sessions = ref([]);

onMounted(async () => {
    const response = await fetch_data(`${Config.backend_address}/sessions/`)
    if (response) {
        sessions.value = response.data.list;
    }
})

async function closeSessions() {
    const response = await fetch_data(
        `${Config.backend_address}/sessions/close/`,
        'POST',
    )
    if (response) {
        UnnecessaryEventEmitter.emit('AlertMessage', {
            title: response.message,
            text: undefined,
            severity: 'info'
        })
        await logout();
    }
}
</script>