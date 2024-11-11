<template>
    <div class="articles-container">
        <Suspense>
            <div v-if="articles">
                <ArticleListCard v-for="article in articles" :key="article.id" :article="article" :isOriginal="!Boolean(original_article_id)"/>
            </div>
            <template #fallback>
                <div>Loading articles...</div>
            </template>
        </Suspense>
        <div v-if="(!articles || articles.length === 0) && !isLoading">There are no articles</div>
        <v-pagination
          :length="pagination.total_pages"
          v-model="pagination.page"
          variant="flat"
        ></v-pagination>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, watch, watchEffect } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fetch_data } from '../../helpers';
import { Config } from '../../settings';
import ArticleListCard from './ListCard.vue';

const route = useRoute();
const router = useRouter();

const articles = ref([]);
const isLoading = ref(true);
const pagination = reactive({
  page: route.query.page ? parseInt(route.query.page as string) : 1,
  total_pages: 1,
})

const props = defineProps({
  original_article_id: {
    type: String,
    required: false,
  },
});

onMounted(fetchArticles);

async function fetchArticles() {
  let url = new URL(`${Config.backend_address}/articles/`)
  url.searchParams.append('page', pagination.page.toString())
  if (props.original_article_id) {
    url.searchParams.append('original_article_id', props.original_article_id)
  }
  try {
    const response = await fetch_data(url.toString());
    if (!response) router.push('/')
    articles.value = response.data.list;
    Object.assign(pagination, response.pagination);
  } finally {
    isLoading.value = false;
  }
}

watch(pagination, (newPagination) => {
    router.push({ query: { ...route.query, page: newPagination.page } });
  },
);
watchEffect(() => {
  fetchArticles();
});
</script>

<style>
.articles-container {
  width: 100%;
}
</style>