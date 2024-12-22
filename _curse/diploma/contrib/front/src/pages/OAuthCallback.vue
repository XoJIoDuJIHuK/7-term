<template>
    <v-dialog v-model="isLoading" persistent hide-overlay>
        <v-card>
            <v-card-title class="justify-center">
                <v-progress-circular
                    indeterminate
                    color="primary"
                    size="64"
                ></v-progress-circular>
            </v-card-title>
            <v-card-subtitle class="text-center">
                Loading, please wait...
            </v-card-subtitle>
        </v-card>
    </v-dialog>
</template>

<script setup lang="ts">
import {fetch_data, fetchPersonalInfo} from "../helpers.ts";
import {onMounted} from "vue";
import {Config} from "../settings.ts";
import {useRoute, useRouter} from "vue-router";
import { ref } from "vue";
import {UnnecessaryEventEmitter} from "../eventBus.ts";

const route = useRoute();
const router = useRouter();
const isLoading = ref(true);

onMounted(async () => {
    const provider = route.params.provider
    const callbackResponse = await fetch_data(
        `${Config.backend_address}/oauth/${provider}/callback/?state=${route.query.state}&code=${route.query.code}`
    );
    if (callbackResponse) {
        UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
            title: undefined,
            text: callbackResponse.detail,
            severity: 'success'
        });
        await fetchPersonalInfo()
        await router.push('/')
    }
})
</script>