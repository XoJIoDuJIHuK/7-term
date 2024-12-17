<template>
    <v-btn
        @click="closeSessions"
        variant="elevated"
        color="red"
    >
        Закрыть все
    </v-btn>
    <v-list lines="one">
        <v-list-item
            v-for="session in sessions"
            :key="session.id"
            :title="`IP-адрес: ${session.ip}. Устройство: ${session.user_agent}`"
            :subtitle="`Дата открытия: ${(new Date(session.created_at)).toLocaleString()}`"
        ></v-list-item>
    </v-list>
</template>

<script setup lang="ts">
import {onMounted, Ref, ref} from 'vue';
import { fetch_data, logout } from '../helpers';
import { Config } from '../settings';
import { UnnecessaryEventEmitter } from '../eventBus';

interface Session {
    id: string;
    ip: string;
    user_agent: string;
    created_at: string;
}

const sessions: Ref<Array<Session>> = ref([]);

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