<template>
    <div class="reports-container">
        <Suspense>
            <div v-if="reports">
                <v-container v-for="report in reports" :key="report.article_id">
                    <v-row>
                        <router-link :to="`/articles/${report.article_id}/report/`">
                            <v-btn>{{ report.article_title }}</v-btn>
                        </router-link>
                    </v-row>
                    <v-row>
                        <v-col>{{ report.status }}</v-col>
                        <v-col>{{ report.text }}</v-col>
                    </v-row>
                </v-container>
            </div>
            <template #fallback>
                <div>Жалобы грузятся...</div>
            </template>
        </Suspense>
        <div v-if="(!reports || reports.length === 0) && !isLoading">Жалоб нет. Хорошая работа</div>
        <v-pagination
          :length="pagination.total_pages"
          v-model="pagination.page"
          variant="flat"
        ></v-pagination>
    </div>
</template>

<script setup lang="ts">
import {onMounted, Ref} from 'vue';
import { fetch_data } from '../helpers';
import { Config } from '../settings';
import { reactive, ref, watch, watchEffect } from 'vue';
import { useRoute, useRouter } from 'vue-router';

type Report = {
    article_id: string;
    article_title: string;
    status: string;
    text: string;
}

const route = useRoute();
const router = useRouter();
const isLoading = ref(true);
const reports: Ref<Array<Report>> = ref([]);
const pagination = reactive({
  page: route.query.page ? parseInt(route.query.page as string) : 1,
  total_pages: 1,
});

onMounted(updateReportsList);

async function updateReportsList() {
    let url = new URL(`${Config.backend_address}/reports/`);
    url.searchParams.append('page', pagination.page.toString());
    const response = await fetch_data(url.toString());
    if (response) {
        reports.value = response.data.list;
        console.log(reports.value)
        Object.assign(pagination, response.pagination);
    }
    isLoading.value = false;
}

watch(pagination, async (newPagination) => {
    await router.push({ query: { ...route.query, page: newPagination.page } });
    isLoading.value = true;
  },
);
watchEffect(async () => {
  await updateReportsList();
});
</script>