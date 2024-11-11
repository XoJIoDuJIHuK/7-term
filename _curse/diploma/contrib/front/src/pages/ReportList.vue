<template>
    <v-container v-for="report in reports" :key="report.article_id">
        <v-row>
            <router-link :to="`/articles/${report.article_id}/report/`">
                <v-btn>{{ report.article_id }}</v-btn>
            </router-link>
        </v-row>
        <v-row>
            <v-col>{{ report.status }}</v-col>
            <v-col>{{ report.reason_text }}</v-col>
        </v-row>
    </v-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { fetch_data } from '../helpers';
import { Config } from '../settings';
import { ref } from 'vue';

const reports = ref([]);

onMounted(async () => {
    const response = await fetch_data(`${Config.backend_address}/reports/`);
    if (response) reports.value = response.data.list;
})
</script>