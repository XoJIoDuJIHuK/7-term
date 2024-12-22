<template>
    <v-app>
        <v-main>
            <v-alert
                v-if="alertObject.isActive"
                :type="alertObject.severity as AlertSeverity"
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
import {AlertMessageParams, AlertSeverity, UnnecessaryEventEmitter} from './eventBus'
import {Config, store, StoreKeys} from './settings';
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

UnnecessaryEventEmitter.on(Config.alertMessageKey, showAlarm)


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
        if (response) store[key as StoreKeys].items = response.data.list;
    }
}

setTimeout(updateStore, 0)

setInterval(updateStore, 60000)
</script>

<style scoped>
.v-alert {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  max-width: 90%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.v-alert-title {
  font-weight: bold;
}

.v-alert.info {
  background-color: #e3f2fd;
  color: #0d47a1;
}

.v-alert.success {
  background-color: #e8f5e9;
  color: #1b5e20;
}

.v-alert.warning {
  background-color: #fff3e0;
  color: #e65100;
}

.v-alert.error {
  background-color: #ffebee; /* Light red background for error */
  color: #c62828; /* Dark red text for error */
}
</style>