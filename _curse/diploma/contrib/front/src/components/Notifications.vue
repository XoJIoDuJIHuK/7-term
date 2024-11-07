<template>
    <v-menu location="end" persistent>
        <template v-slot:activator="{ props }">
            <v-btn
                color="primary"
                dark
                v-bind="props"
            >
                N
            </v-btn>
        </template>

        <v-sheet>
            <v-container>
                <v-row>
                    <v-btn @click="clearNotifications" variant="flat" color="warning">
                        Clear
                    </v-btn>
                </v-row>
                <v-row v-for="n in notifications">
                    {{ n.title }}
                    {{ n.text }}
                </v-row>
                <v-row v-if="notifications.length === 0">No notifications</v-row>
            </v-container>
        </v-sheet>
    </v-menu>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { fetch_data } from '../helpers';
import { Config } from '../settings';
import { UnnecessaryEventEmitter } from '../eventBus';

const router = useRouter();
const notifications = ref([])
const socket = ref(null)

onMounted(async () => {
    try {
        socket.value = new WebSocket(`${Config.websocket_address}/notifications/`)
        socket.value.addEventListener('message', event => {
            const received_notifications = JSON.parse(JSON.parse(event.data)).map(e => JSON.parse(e))
            for (let n of received_notifications) {
                notifications.value.push(n)
            }
        })

    } catch (e) {
        console.log(e)
    }
})

async function clearNotifications() {
    const response = await fetch_data(
        `${Config.backend_address}/notifications/`,
        'PUT'
    )
    console.log(response)
    if (response) {
        notifications.value = []
        UnnecessaryEventEmitter.emit('AlertMessage', {
            title: response.message,
            text: undefined,
            severity: 'info'
        })
    }
}
</script>