<template>
    <div v-if="isLoading">
        Wait
    </div>
    <div v-else>
        You will be redirected soon
    </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { fetch_data } from '../helpers';
import { useRoute, useRouter } from 'vue-router';
import { ref } from 'vue';
import { Config } from '../settings';
import {UnnecessaryEventEmitter} from "../eventBus.ts";

const isLoading = ref(true);
const route = useRoute();
const router = useRouter();

onMounted(async () => {
    const response = await fetch_data(
        `${Config.backend_address}/auth/registration/confirm/?code=${route.query.code}`,
        'POST'
    );
    if (!response) await router.push('/error');
    isLoading.value = false;
    UnnecessaryEventEmitter.emit('AlertMessage', {
        title: 'Почта подтверждена',
        text: undefined,
        severity: 'success'
    })
    await router.push('/');
})
</script>