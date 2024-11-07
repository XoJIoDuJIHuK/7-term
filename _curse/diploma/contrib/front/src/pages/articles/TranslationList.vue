<template>
    <v-container>
      <v-row>
        <h1>Translated articles</h1>
      </v-row>
      <v-row>
        <div>
            <!-- TODO: replace link to translation page -->
            <router-link to="/articles/create">
              <v-btn variant="outlined" color="primary">
                Translate
              </v-btn>
            </router-link>
        </div>
        <div>
          <router-link to="/articles">
            <v-btn class="ml-4" variant="outlined" color="secondary">
              Back
            </v-btn>
          </router-link>
        </div>
      </v-row>
      <v-row>
        <ArticlesList :original_article_id="original_article_id"/>
      </v-row>
    </v-container>
</template>

<script setup lang="ts">
import ArticlesList from '../../components/articles/List.vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const original_article_id = route.params.original_article_id;
</script>