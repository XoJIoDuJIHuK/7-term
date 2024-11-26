<template>
    <h3>Аналитика</h3>
    <v-switch
        v-model="displayModels"
        :label="`Статистика ${displayModels ? 'моделей' : 'промптов'}`"
        class="mt-4"
    ></v-switch>
    <v-container v-for="key of Object.keys(analyticsData)" :key="key">
        <h4>{{ key }}</h4>
        <v-container v-for="param in Object.keys(analyticsData[key])" :key="param">
            {{ param }}: {{ analyticsData[key][param] }}
        </v-container>
    </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { fetch_data } from '../helpers';
import { Config } from '../settings';

const displayModels = ref(true);
const analyticsData = ref({});

onMounted(updateAnalyticsData);

async function updateAnalyticsData() {
    const endpoint = displayModels ? 'models-stats' : 'prompts-stats';
    const response = await fetch_data(`${Config.backend_address}/analytics/${endpoint}/`);
    if (!response) return;
    analyticsData.value = response;
}

watch(displayModels, updateAnalyticsData);
</script>