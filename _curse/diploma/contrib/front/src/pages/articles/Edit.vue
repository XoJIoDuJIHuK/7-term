<template>
    <v-container>
      <v-form ref="form" v-model="valid" lazy-validation>
        <v-text-field
          v-model="article.title"
          label="Название"
          :rules="[rules.required, rules.maxLength(50)]"
          required
        ></v-text-field>
  
        <v-switch
          v-model="useWysiwyg"
          label="Использовать текстовый ввод"
          class="mt-4"
        ></v-switch>
  
        <v-container v-if="useWysiwyg">
            <v-row>
                <v-textarea
                    v-model="article.text"
                    @input="updateMarkdown"
                    class="markdown-textarea"
                    placeholder="Текст статьи"
                    auto-grow
                ></v-textarea>
            </v-row>
            <v-row>
                <div
                    v-html="renderedMarkdown || '<p>Предпросмотр текста</p>'"
                    class="markdown-renderer"
                ></div>
            </v-row>
        </v-container>
        <div v-else>
          <v-file-input
            v-model="article.file"
            label="Загрузите файл (.txt, .md)"
            accept=".txt,.md"
            @change="handleFileChange"
            :rules="[rules.required]"
            required
          ></v-file-input>
        </div>
  
        <v-select
          v-if="!route.params.article_id"
          v-model="article.language_id"
          :items="store.languages.getSelectItems()"
          label="Язык (необязательно)"
          chips
          clearable
        ></v-select>
  
        <v-btn color="primary" :disabled="!valid" @click="saveArticle">
          {{ isEditing ? 'Изменить' : 'Создать' }} статью
        </v-btn>
      </v-form>
    </v-container>
</template>
  
<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { Config, store, validationRules as rules } from '../../settings';
import { useRoute, useRouter } from 'vue-router';
import { fetch_data } from '../../helpers';
import { get_article } from './helpers';
import { UnnecessaryEventEmitter } from '../../eventBus';
import { marked } from 'marked';

const form = ref(null);
const valid = ref(false);
const useWysiwyg = ref(true);
const article = reactive({
    title: '',
    text: '',
    file: null,
    language_id: null,
});

const route = useRoute();
const router = useRouter();

const isEditing = ref(false);


const localText = ref('');
const emit = defineEmits(['update:text']);
const renderedMarkdown = ref('');
const updateMarkdown = async () => {
    emit('update:text', localText.value);
    renderedMarkdown.value = await marked.parse(localText.value || '')
}
watch(() => article.text, (newValue) => {
    localText.value = newValue
    updateMarkdown()
}, { immediate: true })


onMounted(async () => {
    const article_id = route.params.article_id
    if (article_id) {
        isEditing.value = true;
        try {
            const response = await get_article(article_id as string)
            if (!response) {
              await router.push('/error')
              return
            }
            Object.assign(article, response);
            } catch (error) {
            console.error('Error fetching article:', error);
        }
    }
});

const handleFileChange = async (file: any) => {
    if (file) {
        const reader = new FileReader();
        reader.onload = (e: ProgressEvent) => {
            article.text = (e.target! as FileReader).result as string;
        };
        reader.readAsText(file.target.files[0]);
    }
};

const saveArticle = async () => {
    console.log(form, typeof form)
    //@ts-ignore
    if (form!.value!.validate()) {
        try {
            const apiUrl = isEditing.value
                ? `${Config.backend_address}/articles/${route.params.article_id}/`
                : `${Config.backend_address}/articles/`;
            const method = isEditing.value ? 'PUT' : 'POST';
            const response = await fetch_data(
                apiUrl,
                method,
                JSON.stringify({
                    title: article.title,
                    text: article.text,
                    language_id: article.language_id
                })
            )
            if (response) {
                UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
                    title: 'Статья сохранена',
                    text: undefined,
                    severity: 'info'
                })
                await router.push(`/articles/${response.data.article.id}/get`)
            }
        } catch (error) {
            console.error('Error saving article:', error);
        }
    }
};
</script>

<style lang="css" scoped>
.markdown-renderer {
    min-height: 32px;
    width: 100%;
    padding: 16px;
    border: 1px black;
    border-radius: 8px;
    background-color: #e9e9e9;
}
</style>