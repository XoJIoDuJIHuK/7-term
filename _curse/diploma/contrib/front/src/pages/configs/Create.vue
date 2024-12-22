<template>
    <ConfigEditor
        :currentEditConfig="createdConfig"
        :onSave="() => { createConfig() }"
        :onCancel="() => { router.push('/configs') }"
    ></ConfigEditor>
</template>
  
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { fetch_data } from '../../helpers';
import { Config, store } from '../../settings';
import ConfigEditor from '../../components/configs/Editor.vue';
import {UnnecessaryEventEmitter} from "../../eventBus.ts";

const router = useRouter();

const createdConfig = ref({
    name: '',
    model_id: store.models.items.length > 0 ? store.models.items[0].id : '',
    prompt_id: store.prompts.items.length > 0 ? store.prompts.items[0].id : '',
    language_ids: [],
})

async function createConfig() {
    const response = await fetch_data(
        `${Config.backend_address}/configs/`,
        'POST',
        JSON.stringify(createdConfig.value),
    );
    if (response) {
        UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
            title: undefined,
            text: 'Конфиг создан',
            severity: 'info'
        })
        await router.push('/configs')
    }
}
</script>