<template>
    <v-container>
      <v-form ref="form" v-model="valid" lazy-validation>
        <v-text-field
          v-model="article.title"
          label="Title"
          :rules="[rules.required]"
          required
        ></v-text-field>
  
        <v-switch
          v-model="useWysiwyg"
          label="Use text editor"
          class="mt-4"
        ></v-switch>
  
        <div v-if="useWysiwyg">
          <div id="text-editor">
            <textarea v-model="article.text"></textarea>
          </div>
        </div>
        <div v-else>
          <v-file-input
            v-model="article.file"
            label="Upload Text File"
            accept=".txt"
            @change="handleFileChange"
            :rules="[rules.required]"
            required
          ></v-file-input>
        </div>
  
        <v-select
          v-if="!route.params.article_id"
          v-model="article.language_id"
          :items="store.languages.getSelectItems()"
          label="Language (Optional)"
          chips
          clearable
        ></v-select>
  
        <v-btn color="primary" :disabled="!valid" @click="saveArticle">
          {{ isEditing ? 'Update' : 'Create' }} Article
        </v-btn>
      </v-form>
    </v-container>
</template>
  
<script setup>
  import { ref, reactive, onMounted } from 'vue';
  import { Config, store } from '../../settings';
  import { useRoute, useRouter } from 'vue-router';
  import { fetch_data } from '../../helpers';
  import { get_article } from './helpers';
  import { UnnecessaryEventEmitter } from '../../eventBus';

  
  const form = ref(null);
  const valid = ref(false);
  const useWysiwyg = ref(true);
  const article = reactive({
    title: '',
    text: '',
    file: null,
    language_id: null,
  });
  
  const rules = {
    required: (value) => !!value || 'Required.',
  };
  
  const route = useRoute();
  const router = useRouter();
  
  const isEditing = ref(false);
  
  onMounted(async () => {
    const article_id = route.params.article_id
    if (article_id) {
      isEditing.value = true;
      try {
        const response = await get_article(article_id)
        if (!response) {
          router.push('/error')
          return
        }
        Object.assign(article, response);
      } catch (error) {
        console.error('Error fetching article:', error);
      }
    }
  });
  
  const handleFileChange = async (file) => {
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        article.text = e.target.result;
      };
      reader.readAsText(file);
    }
  };
  
  const saveArticle = async () => {
    if (form.value.validate()) {
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
          UnnecessaryEventEmitter.emit('AlertMessage', {
            title: 'Статья сохранена',
            text: undefined,
            severity: 'info'
          })
          router.push(`/articles/${response.data.article.id}/get`)
        }
      } catch (error) {
        console.error('Error saving article:', error);
      }
    }
  };
</script>

<style lang="css" scoped>
#text-editor textarea {
  width: 100%;
  border: 1px solid black;
  border-radius: 8px;
  padding: 8px;
}
</style>