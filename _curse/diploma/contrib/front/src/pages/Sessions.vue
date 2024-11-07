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
import { useRouter } from 'vue-router';

const sessions = ref([]);
const router = useRouter();

onMounted(async () => {
    const response = await fetch_data(`${Config.backend_address}/sessions/`)
    if (response) {
        sessions.value = response.data.list;
    }
})

async function closeSessions() {
    await fetch_data(
        `${Config.backend_address}/sessions/close/`,
        'POST',
    )
    await logout(router);
}
</script>