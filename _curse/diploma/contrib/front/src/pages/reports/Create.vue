<template>
    <v-container>
        <v-row>
            <h2>Create report</h2>
        </v-row>
        <v-row>
            <v-select
                :items="store.reportReasons.getSelectItems()"
                v-model="reportData.reason_id"
            ></v-select>
        </v-row>
        <v-row>
            <v-textarea v-model="reportData.text" label="Text">

            </v-textarea>
        </v-row>
        <v-row>
            <v-btn @click="createReport">Save</v-btn>
        </v-row>
    </v-container>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import { store } from '../../settings';
import { fetch_data } from '../../helpers';
import { Config } from '../../settings';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const reportData = reactive({
    text: '',
    reason_id: 1
});

async function createReport() {
    const response = await fetch_data(
        `${Config.backend_address}/articles/${route.params.article_id}/report/`,
        'POST',
        JSON.stringify(reportData),
    )
    if (response) router.push(`/articles/${route.params.article_id}/report`)
}
</script>