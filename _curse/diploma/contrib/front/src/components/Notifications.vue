<template>
    <v-menu location="end" persistent>
        <template v-slot:activator="{ props }">
            <v-btn
                color="primary"
                dark
                v-bind="props"
                class="notification-button"
            >
                <v-icon>mdi-bell</v-icon>
                <v-chip
                    v-if="notifications.length > 0"
                    color="red"
                    label
                    class="notification-chip"
                >
                    {{ notifications.length }}
                </v-chip>
            </v-btn>
        </template>

        <v-sheet elevation="2" class="notification-sheet">
            <v-container>
                <v-row justify="space-between" align="center">
                    <v-btn @click="clearNotifications" variant="flat" color="warning">
                        Очистить
                    </v-btn>
                </v-row>
                <v-divider class="my-4"></v-divider>
                <v-container v-if="notifications.length > 0" class="notifications-container pa-0">
                    <v-card
                        v-for="(notification, index) in notifications"
                        :key="index"
                        class="notification-card mb-3"
                        elevation="1"
                    >
                        <v-card-title class="text-subtitle-1 font-weight-bold pb-1">
                            {{ notification.title }}
                        </v-card-title>
                        <v-card-text class="pt-1">
                            <div class="text-body-2">{{ notification.text }}</div>
                            <div class="text-caption text-grey mt-2">
                                {{ formatRelativeTime(notification.created_at) }}
                            </div>
                        </v-card-text>
                    </v-card>
                </v-container>
                <v-row v-else>
                    <v-col class="text-center">Уведомлений нет</v-col>
                </v-row>
            </v-container>
        </v-sheet>
    </v-menu>
</template>

<script setup lang="ts">
import { onMounted, Ref, ref } from 'vue';
import { formatDistanceToNow } from 'date-fns';
import { ru } from 'date-fns/locale';
import { fetch_data } from '../helpers';
import { Config } from '../settings';
import { UnnecessaryEventEmitter } from '../eventBus';

interface Notification {
    title: string;
    text: string;
    type: string;
    created_at: string;
}

const notifications: Ref<Array<Notification>> = ref([]);
const socket: Ref<null | WebSocket> = ref(null);

const formatRelativeTime = (timestamp: string): string => {
    try {
        return formatDistanceToNow(new Date(timestamp), {
            addSuffix: true,
            locale: ru
        });
    } catch {
        return '';
    }
};

onMounted(async () => {
    const userRole = JSON.parse(localStorage.getItem(Config.userInfoProperty) as string).role;
    const response = await fetch_data(`${Config.backend_address}/notifications/`);
    if (response) notifications.value = response.data.list;

    if (userRole === Config.userRoles.admin) return;

    try {
        socket.value = new WebSocket(`${Config.websocket_address}/notifications/`);
        socket.value.addEventListener('message', event => {
            const notification = JSON.parse(event.data);
            notification.timestamp = new Date().toISOString(); // Add timestamp to new notifications

            UnnecessaryEventEmitter.emit('AlertMessage', {
                title: notification.title,
                text: notification.text,
                severity: notification.type
            });
            notifications.value.push(notification);
        });
    } catch (e) {
        console.log('Notifications websocket error:', e);
    }
});

async function clearNotifications() {
    const response = await fetch_data(
        `${Config.backend_address}/notifications/`,
        'PUT',
    );
    if (response) {
        notifications.value = [];
        UnnecessaryEventEmitter.emit('AlertMessage', {
            title: response.message,
            text: undefined,
            severity: 'info'
        });
    }
}
</script>

<style scoped>
.notification-button {
    position: relative;
}

.notification-chip {
    position: absolute;
    top: -5px;
    right: -10px;
}

.notification-sheet {
    display: flex;
    flex-direction: column;
    margin-top: 50px;
    z-index: 9001;
    min-width: 350px;
    max-width: 400px;
}

.notifications-container {
    max-height: 400px;
    overflow-y: auto;
}

.notification-card {
    width: 100%;
}
</style>