<template>
    <v-card class="article-card">
        <v-card-title>
            {{ config.name }}
            <v-spacer></v-spacer>
            <span class="article-flag">
                {{ store.languages.getValue(config.language_id) }}
            </span>
        </v-card-title>
        <v-card-actions>
          <v-btn variant="tonal" color="green" @click="UnnecessaryEventEmitter.emit(
            'ShowConfigEditPopup', config.id
            )">
            <v-icon icon="mdi-pencil"/>
          </v-btn>
          <v-btn variant="tonal" color="red" @click="() => { delete_config(config.id) }">
            <v-icon icon="mdi-delete"/>
          </v-btn>
        </v-card-actions>
    </v-card>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { store } from '../../settings';
import { VCard, VCardTitle, VSpacer, VIcon } from 'vuetify/components';
import { fetch_data } from '../../helpers';
import { Config } from '../../settings';
import { UnnecessaryEventEmitter } from '../../eventBus';

const router = useRouter();
//@ts-ignore
const props = defineProps({
  config: {
    type: Object,
    required: true,
  },
});

async function delete_config(article_id: string) {
  const result = await fetch_data(
    `${Config.backend_address}/configs/${article_id}/`,
    'DELETE'
  )
  if (result) {
    UnnecessaryEventEmitter.emit('AlertMessage', {
      title: undefined,
      text: 'Конфиг успешно удалён',
      severity: 'success'
    })
    location.reload()
  } else {
    await router.push('/')
  }
}
</script>