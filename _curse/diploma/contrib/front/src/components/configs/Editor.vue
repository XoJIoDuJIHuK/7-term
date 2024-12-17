<template>
    <v-container>
        <v-row v-if="currentEditConfig.id">
            <h3>{{ currentEditConfig.name }}</h3>
        </v-row>
        <v-row v-if="!currentEditConfig.id">
            <h4>Название</h4>
            <v-text-field
                v-model="currentEditConfig.name"
            ></v-text-field>
        </v-row>
        <v-row>
            <h4>Модель</h4>
            <v-select
                v-model="currentEditConfig.model_id"
                clearable
                :items="store.models.getSelectItems()"
            ></v-select>
        </v-row>
        <v-row>
            <h4>Стиль</h4>
            <v-select
                v-model="currentEditConfig.prompt_id"
                clearable
                :items="store.prompts.getSelectItems()"
            ></v-select>
        </v-row>
        <v-row>
            <h4>Языки</h4>
            <v-select
                v-model="currentEditConfig.language_ids"
                clearable
                multiple
                :items="store.languages.getSelectItems()"
            ></v-select>
        </v-row>
        <v-row>
            <v-btn @click="onCancel" color="error">
                Отмена
            </v-btn>
            <v-btn @click="onSave" color="primary">
                Сохранить
            </v-btn>
        </v-row>
    </v-container>
</template>

<script setup lang="ts">
import { store } from '../../settings';

//@ts-ignore
const props = defineProps({
    currentEditConfig: {
        type: Object,
        required: true,
    },
    onSave: {
        type: Function,
        required: true,
    },
    onCancel: {
        type: Function,
        required: true,
    },
})
</script>