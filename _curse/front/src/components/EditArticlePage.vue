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
          label="Use WYSIWYG Editor"
          class="mt-4"
        ></v-switch>
  
        <div v-if="useWysiwyg">
          <!-- Replace with your actual WYSIWYG editor component -->
          <div id="wysiwyg-editor">
            <p>WYSIWYG editor would go here (e.g., using vue-quill-editor)</p>
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
          v-model="article.language_id"
          :items="Object.entries(languages).map(e => e[1])"
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
  import { Config, languages } from '../settings';
  import { useRoute, useRouter } from 'vue-router';
  import axios from 'axios';
import { fetch_data } from '../helpers';
  
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
  console.log(Array.from(languages))
  
  const isEditing = ref(false); // Flag to indicate whether we're editing or creating
  
  onMounted(async () => {
    if (route.params.id) {
      isEditing.value = true;
      try {
        const response = await fetch_data(
            `${Config.backend_address}/articles/${route.params.id}/`,
            'GET'
        );
        Object.assign(article, response.data);
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
      const formData = new FormData();
      formData.append('title', article.title);
      formData.append('text', article.text);
      formData.append('language_id', article.language_id);
  
      try {
        const apiUrl = isEditing.value
          ? `${Config.backend_address}/articles/${route.params.id}/`
          : `${Config.backend_address}/articles/`;
        const method = isEditing.value ? 'put' : 'post';
        // const response = await axios[method](apiUrl, formData, {
        //   headers: {
        //     'Content-Type': 'multipart/form-data',
        //   },
        // });
        const response = await fetch_data(
            apiUrl, method, data
        )
        console.log('Article saved successfully:', response.data);
        router.push('/articles/');
      } catch (error) {
        console.error('Error saving article:', error);
      }
    }
  };
</script>