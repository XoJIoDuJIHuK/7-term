<script setup lang="ts">
import ArticlesList from './ArticlesList.vue';
</script>

<template>
    <h1>Articles</h1>
    <div>
        <router-link to="/articles/create">Create</router-link>
    </div>
    <ArticlesList/>
</template>