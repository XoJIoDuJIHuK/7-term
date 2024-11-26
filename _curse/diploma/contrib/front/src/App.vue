<template>
    <v-app>
        <v-main>
        <v-alert
            v-if="alertObject.isActive"
            :type="alertObject.severity"
            dismissible
            @close="alertObject.isActive = false"
        >
            <v-alert-title>{{ alertObject.title }}</v-alert-title>
            {{ alertObject.text }}
        </v-alert>
        <router-view />
        </v-main>
    </v-app>
</template>

<script setup lang="ts">
import { AlertMessageParams, UnnecessaryEventEmitter } from './eventBus'
import { Config, store } from './settings';
import { fetch_data } from './helpers';
import { reactive } from 'vue'

const alertObject = reactive({
    title: '',
    text: '',
    isActive: false,
    severity: 'info'
})

function showAlarm(params: AlertMessageParams) {
    Object.assign(alertObject, params)
    alertObject.isActive = true
    setTimeout(() => {
        alertObject.isActive = false
    }, 2000)
}

UnnecessaryEventEmitter.on('AlertMessage', showAlarm)


async function updateStore() {
    const urls = [
        ['models', 'models'], ['languages', 'languages'], ['prompts', 'prompts/public'], 
        ['reportReasons', 'report-reasons']
    ]
    for (let [key, url] of urls) {
        const response = await fetch_data(
            `${Config.backend_address}/${url}/`,
            'GET',
            undefined,
            false
        );
        if (response) store[key].items = response.data.list;
    }
}

setTimeout(updateStore, 0)

setInterval(updateStore, 60000)
</script>