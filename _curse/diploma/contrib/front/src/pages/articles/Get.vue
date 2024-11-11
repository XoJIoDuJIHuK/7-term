<template>
    <v-container v-if="article.original_article_id === null && translationConfigState.isVisible">
        <v-row>
            <h4>Config</h4>
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
            <h4>Model</h4>
            <v-select
                v-model="translationConfigState.model_id"
                clearable
                :items="store.models.getSelectItems()"
            ></v-select>
        </v-row>
        <v-row>
            <h4>Prompt</h4>
            <v-select
                v-model="translationConfigState.prompt_id"
                clearable
                :items="store.prompts.getSelectItems()"
            ></v-select>
        </v-row>
        <v-row>
            <h4>Languages</h4>
            <v-select
                v-model="translationConfigState.language_ids"
                clearable
                multiple
                :items="store.languages.getSelectItems()"
            ></v-select>
        </v-row>
        <v-row>
            <v-btn variant="elevated" color="error" @click="translationConfigState.isVisible = false">
                Cancel
            </v-btn>
            <v-btn variant="elevated" color="primary" @click="startTranslation">
                Translate
            </v-btn>
        </v-row>
    </v-container>
    <v-sheet
        class="d-flex align-center justify-center flex-wrap text-center mx-auto px-4"
        elevation="4"
        max-width="800"
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
                <div>{{ store.languages.getValue(article.language_id) ? store.languages.getValue(article.language_id).iso_code : 'Language not specified' }}</div>
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
                <router-link :to="`/articles/${article.id}/report/${article.report_exists ? '' : 'create'}`">
                    <v-btn variant="tonal" color="error">
                        <v-icon icon="mdi-bug" aria-hidden="false"/>
                    </v-btn>
                </router-link>
            </v-row>
            <v-row>
                {{ article.text }}
            </v-row>
        </v-container>
    </v-sheet>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { get_article } from './helpers';
import { useRoute, useRouter } from 'vue-router';
import { Config, store } from '../../settings';
import { fetch_data } from '../../helpers';
import { UnnecessaryEventEmitter } from '../../eventBus';

const route = useRoute();
const router = useRouter();

const article = reactive({
    title: 'Not loaded',
    text: 'Not loaded',
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
const configs = ref([])

onMounted(async () => {
    const article_id = String(route.params.article_id)
    let response = await get_article(article_id)
    if (!response) {
        router.push('/error')
    }
    Object.assign(article, response)
    console.log(article.original_article_id);
    

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
        UnnecessaryEventEmitter.emit('AlertMessage', {
            title: result.message,
            text: undefined,
            severity: 'info'
        })
        translationConfigState.isVisible = false;
    }
}
</script>