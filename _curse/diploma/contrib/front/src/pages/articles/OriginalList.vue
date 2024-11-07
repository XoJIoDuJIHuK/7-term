<template>
    <v-container style="width: 100%;">
        <v-row>
            <h1>Articles</h1>
        </v-row>
        <v-row>
            <router-link to="/articles/create">
                <v-btn variant="outlined" color="primary">
                    Create
                </v-btn>
            </router-link>
        </v-row>
        <v-row>
            <ArticlesList/>
        </v-row>
    </v-container>
</template>

<script setup lang="ts">
import ArticlesList from '../../components/articles/List.vue';
</script>