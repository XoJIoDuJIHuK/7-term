<template>
    <v-card class="article-card">
        <v-card-title>
            {{ article.title }}
            <v-spacer></v-spacer>
            <span class="article-language">
                {{ store.languages.getValue(article.language_id) === null ? '' : store.languages.getValue(article.language_id).iso_code }}
            </span>
        </v-card-title>
        <v-card-text>
            <p>Created at: {{ (new Date(article.created_at)).toLocaleString() }}</p>
            <p>Liked: {{ article.like === null ? 'No data' : article.like ? 'Yes' : 'No' }}</p>
        </v-card-text>
        <v-card-actions>
          <router-link :to="`/articles/${article.id}/get`">
            <v-btn variant="tonal" color="blue">
              <v-icon icon="mdi-eye"/>
            </v-btn>
          </router-link>
          <router-link :to="`/articles/${article.id}/update`" v-if="isOriginal">
            <v-btn variant="tonal" color="green">
              <v-icon icon="mdi-pencil"/>
            </v-btn>
          </router-link>
          <v-btn variant="tonal" color="red" @click="() => { delete_article(article.id) }">
            <v-icon icon="mdi-delete"/>
          </v-btn>
          <router-link :to="`/articles/${article.id}/translations`" v-if="isOriginal">
            <v-btn variant="tonal" color="blue">
              <v-icon icon="mdi-earth"/>
            </v-btn>
          </router-link>
        </v-card-actions>
    </v-card>
</template>

<script setup lang="ts">
import { store } from '../../settings';
import { VCard, VCardTitle, VCardText, VSpacer, VIcon } from 'vuetify/components';
import { fetch_data } from '../../helpers';
import { Config } from '../../settings';
import { UnnecessaryEventEmitter } from '../../eventBus';

const props = defineProps({
    article: {
        type: Object,
        required: true,
    },
    isOriginal: {
        type: Boolean,
        required: true,
    }
});

async function delete_article(article_id: string) {
    const result = await fetch_data(
      `${Config.backend_address}/articles/${article_id}/`,
      'DELETE',
    )
    if (result) {
      UnnecessaryEventEmitter.emit('AlertMessage', {
        title: undefined,
        text: 'Статья успешно удалена',
        severity: 'success'
      })
      location.reload()
    }
}
</script>