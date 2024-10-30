<template>
    <div class="articles-container">
        <Suspense>
            <div v-if="articles">
                <ArticleListCard v-for="article in articles" :key="article.id" :article="article"/>
            </div>
            <template #fallback>
                <div>Loading articles...</div>
            </template>
        </Suspense>
        <div v-if="!articles && !isLoading">There are no articles</div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { fetch_data } from '../helpers';
import { Config } from '../settings';
import ArticleListCard from './ArticleListCard.vue';

const articles = ref(null);
const isLoading = ref(true);

onMounted(async () => {
  try {
    const response = await fetch_data(
        `${Config.backend_address}/articles/`,
        'GET'
    );
    articles.value = response.data.list;
  } finally {
    isLoading.value = false;
  }
});

</script>