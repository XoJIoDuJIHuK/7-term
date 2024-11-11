<template>
    <v-container>
        <v-row><h1>Page not found</h1></v-row>
        <v-row><v-btn color="red" @click="logout">Logout</v-btn></v-row>
    </v-container>
</template>

<script setup>
import { logout } from '../helpers';
</script>