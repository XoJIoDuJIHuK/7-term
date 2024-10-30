<template>
    <v-card class="article-card">
        <v-card-title>
            <router-link :to="`/articles/${article.id}`">{{ article.title }}</router-link>
            <v-spacer></v-spacer>
            <span class="article-flag">
                {{ languages[article.language_id] }}
            </span>
        </v-card-title>
        <v-card-text>
            <p>Created at: {{ formatDate(article.created_at) }}</p>
            <p>Liked: {{ article.like === null ? 'No data' : article.like ? 'Yes' : 'No' }}</p>
        </v-card-text>
    </v-card>
</template>

<script setup>
import { computed } from 'vue';
import { languages } from '../settings';
import { VCard, VCardTitle, VCardText, VSpacer, VIcon } from 'vuetify/components';

const props = defineProps({
  article: {
    type: Object,
    required: true,
  },
});
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString();
};
</script>