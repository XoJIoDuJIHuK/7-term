<template>
    <div v-if="currentEditConfig.id">
        <ConfigEditor
            :currentEditConfig="currentEditConfig"
            :onSave="() => { saveConfig() }"
            :onCancel="() => { currentEditConfig = {id: undefined} }"
        ></ConfigEditor>
    </div>
    
    <div class="articles-container">
        <Suspense>
            <div v-if="configs">
                <ConfigListCard v-for="config in configs" :key="config.id" :config="config"/>
            </div>
            <template #fallback>
                <div>Идёт загрузка...</div>
            </template>
        </Suspense>
        <div v-if="(!configs || configs.length === 0) && !isLoading">Конфигураций нет</div>
    </div>
</template>

<script setup lang="ts">
import {ref, onMounted, Ref} from 'vue';
import { useRouter } from 'vue-router';
import { fetch_data } from '../../helpers';
import { Config } from '../../settings';
import ConfigListCard from './ListCard.vue';
import { UnnecessaryEventEmitter } from '../../eventBus';
import ConfigEditor from './Editor.vue';

type Config = {
    id: string | undefined;
}

const router = useRouter();

const configs: Ref<Array<Config>> = ref([]);
const isLoading = ref(true);

const currentEditConfig: Ref<Config> = ref({id: undefined});

onMounted(fetchConfigs);

async function saveConfig() {
    const response = await fetch_data(
        `${Config.backend_address}/configs/${currentEditConfig.value.id}/`,
        'PUT',
        JSON.stringify(currentEditConfig.value)
    );
    if (response) {
        UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
            title: undefined,
            text: 'Конфиг обновлён',
            severity: 'success'
        })
        location.reload()
    }
}

async function fetchConfigs() {
    let url = new URL(`${Config.backend_address}/configs/`)
    try {
        const response = await fetch_data(url.toString());
        if (!response) await router.push('/')
        configs.value = response.data.list
    } finally {
        isLoading.value = false;
    }
}

UnnecessaryEventEmitter.on('ShowConfigEditPopup', config_id => {
    Object.assign(currentEditConfig.value, configs.value.find((config: Config) => config.id === config_id));
})
</script>

<style>
.articles-container {
  width: 100%;
}
</style>