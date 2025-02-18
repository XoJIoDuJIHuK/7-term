<template>
    <v-container class="translation-form-wrapper" v-if="article.original_article_id === null && translationConfigState.isVisible">
        <v-card class="mx-auto px-6 py-8 translation-form">
            <v-container>
                <v-row>
                    <h4>Конфиги</h4>
                    <v-select
                        clearable
                        :items="configs.map(config => ({ value: config, title: config.name }))"
                        @update:model-value="(newValue) => {
                        translationConfigState.model_id = newValue.model_id;
                        translationConfigState.prompt_id = newValue.prompt_id;
                        translationConfigState.language_ids = newValue.language_ids;
                    }"
                    ></v-select>
                </v-row>
                <v-row>
                    <h4>Модель</h4>
                    <v-select
                        v-model="translationConfigState.model_id"
                        clearable
                        :items="store.models.getSelectItems()"
                    ></v-select>
                </v-row>
                <v-row>
                    <h4>Промпт</h4>
                    <v-select
                        v-model="translationConfigState.prompt_id"
                        clearable
                        :items="store.prompts.getSelectItems()"
                    ></v-select>
                </v-row>
                <v-row>
                    <h4>Языки</h4>
                    <v-select
                        v-model="translationConfigState.language_ids"
                        clearable
                        multiple
                        :items="store.languages.getSelectItems()"
                    ></v-select>
                </v-row>
                <v-row>
                    <v-btn variant="elevated" color="error" @click="translationConfigState.isVisible = false">
                        Отмена
                    </v-btn>
                    <v-btn variant="elevated" color="primary" @click="startTranslation">
                        Начать перевод
                    </v-btn>
                </v-row>
            </v-container>
        </v-card>
    </v-container>
    <v-sheet
        class="text-sheet"
        elevation="4"
        max-width="80vw"
        width="100%"
        rounded
    >
        <v-container>
            <v-row>
                <h2 class="font-weight-black">{{ article.title }}</h2>
                <h4>{{ (new Date(article.created_at)).toLocaleString() }}</h4>
                <div v-if="article.original_article_id !== null">
                    <div v-if="article.like === null">
                        <v-btn @click="() => { setLike(true) }">
                            <v-icon icon="mdi-thumb-up-outline"></v-icon>
                        </v-btn>
                        <v-btn @click="() => { setLike(false) }">
                            <v-icon icon="mdi-thumb-down-outline"></v-icon>
                        </v-btn>
                    </div>
                    <div v-else>
                        <v-btn @click="() => { setLike(null) }">
                            <v-icon :icon="article.like ? 'mdi-thumb-up' : 'mdi-thumb-down'"></v-icon>
                        </v-btn>
                    </div>
                </div>
                <div>{{ store.languages.getValue(article.language_id) ? store.languages.getValue(article.language_id)!.iso_code : 'Язык не указан' }}</div>
                <router-link :to="`/articles/${article.id}/update`" v-if="article.original_article_id === null">
                    <v-btn variant="tonal" color="green">
                        <v-icon icon="mdi-pencil" aria-hidden="false"/>
                    </v-btn>
                </router-link>
                <v-btn 
                    @click="translationConfigState.isVisible = true"
                    v-if="article.original_article_id === null"
                    variant="tonal"
                    color="blue"
                ><v-icon icon="mdi-earth"/></v-btn>
                <router-link v-if="article.original_article_id" :to="`/articles/${article.id}/report/${article.report_exists ? '' : 'create'}`">
                    <v-btn variant="tonal" color="error">
                        <v-icon icon="mdi-bug" aria-hidden="false"/>
                    </v-btn>
                </router-link>
            </v-row>
            <v-row>
                <div v-html="renderedMarkdown" class="markdown-renderer"></div>
            </v-row>
        </v-container>
    </v-sheet>
</template>

<script setup lang="ts">
import {onMounted, reactive, Ref, ref} from 'vue';
import { get_article } from './helpers';
import { useRoute, useRouter } from 'vue-router';
import { Config, store } from '../../settings';
import { fetch_data } from '../../helpers';
import { UnnecessaryEventEmitter } from '../../eventBus';
import { marked } from 'marked';

interface Config {
    name: string;
    text: string;
}

const route = useRoute();
const router = useRouter();
const renderedMarkdown = ref('');

const article = reactive({
    title: 'Не загружен',
    text: 'Не загружен',
    language_id: null,
    created_at: '',
    original_article_id: null,
    like: null as boolean | null,
    id: null,
    report_exists: false,
})
const translationConfigState = reactive({
    isVisible: false,
    model_id: undefined,
    prompt_id: undefined,
    language_ids: [],
})
const configs: Ref<Array<Config>> = ref([])

onMounted(async () => {
    const article_id = String(route.params.article_id)
    let response = await get_article(article_id)
    if (!response) {
        await router.push('/error')
    }
    Object.assign(article, response)
    renderedMarkdown.value = await marked(article.text);
    

    response = await fetch_data(`${Config.backend_address}/configs/`)
    if (response) {
        configs.value = response.data.list
    }
})

async function setLike(newValue: boolean | null) {
    const response = await fetch_data(
        `${Config.backend_address}/articles/${article.id}/like/`,
        'PATCH',
        JSON.stringify({
            like: newValue
        })
    )
    if (response) article.like = newValue
}

async function startTranslation() {
    const result = await fetch_data(
        `${Config.backend_address}/translation/`,
        'POST',
        JSON.stringify({
            article_id: article.id,
            model_id: translationConfigState.model_id,
            prompt_id: translationConfigState.prompt_id,
            source_language_id: article.language_id,
            target_language_ids: translationConfigState.language_ids
        }),
    )
    if (result) {
        UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
            title: result.message,
            text: undefined,
            severity: 'info'
        })
        translationConfigState.isVisible = false;
    }
}
</script>

<style scoped>
.text-sheet {
    display: flex;
    align-content: center;
    justify-content: center;
    flex-wrap: wrap;
    text-wrap: wrap;
    padding: 4px;
    margin: 16px auto 16px auto;
}
.markdown-renderer {
    font-family: Arial, sans-serif;
    text-align: left;
    line-height: 1.6;
    word-wrap: break-word;
    overflow-wrap: break-word;
    white-space: normal;
    max-width: 100%;
}

.translation-form {
    position: fixed;
    top: 100px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1000;
    width: 50%;
    max-width: 90%;
    border-radius: 8px;
}

.translation-form-wrapper {
    z-index: 999;
    margin: 0;
    padding: 0;
    position: fixed;
    width: 100vw;
    max-width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
}
</style>