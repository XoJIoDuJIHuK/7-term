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

const isLoading = ref(true);
const route = useRoute();
const router = useRouter();

onMounted(async () => {
    const response = await fetch_data(
        `${Config.backend_address}/auth/restore-password/confirm/?code=${route.query.code}`
    );
    if (!response) {
        router.push('/error');
    }
    isLoading.value = false;
    router.push('/');
})
</script>