<template>
    <v-container>
        <v-row>
            <h1>Переводы статьи</h1>
        </v-row>
        <v-row>
            <ArticlesList :original_article_id="original_article_id as string"/>
        </v-row>
    </v-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import ArticlesList from '../../components/articles/List.vue';
import { useRoute, useRouter } from 'vue-router';
import { ref } from 'vue';
import { fetch_data } from '../../helpers';
import { Config } from '../../settings';


const route = useRoute();
const router = useRouter();
const original_article_id = route.params.original_article_id;

const originalArticleName = ref('');

onMounted(async () => {
    const response = await fetch_data(`${Config.backend_address}/articles/${original_article_id}/`);
    if (response) {
        originalArticleName.value = response.data.article.title;
    } else {
        await router.push('/error');
    }
});
</script>