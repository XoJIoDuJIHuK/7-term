<template>
    <v-container style="width: 100%;">
        <v-row>
            <h1>Настройки переводчика</h1>
        </v-row>
        <v-row>
            <router-link to="/configs/create">
                <v-btn variant="outlined" color="primary">
                    Создать
                </v-btn>
            </router-link>
        </v-row>
        <v-row>
            <ConfigsList/>
        </v-row>
    </v-container>
</template>

<script setup lang="ts">
import ConfigsList from '../../components/configs/List.vue';
</script>