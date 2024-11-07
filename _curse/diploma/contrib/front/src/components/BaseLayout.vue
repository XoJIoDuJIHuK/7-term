<template>
    <header>
        <nav>
            <v-container>
                <v-row>
                    <router-link to="/articles">
                        <v-btn class="mr-4" variant="outlined">Articles</v-btn>
                    </router-link>
                    <router-link to="/configs">
                        <v-btn class="mr-4" variant="outlined">Configs</v-btn>
                    </router-link>
                    <Notifications/>
                    <UserMenu/>
                </v-row>
            </v-container>
        </nav>
    </header>
    <main>
        <router-view /> 
    </main>
</template>

<script setup lang="ts">
import UserMenu from './UserMenu.vue';
import Notifications from './Notifications.vue';
</script>

<style scoped>
main {
    margin-top: 100px;
}

header {
    position: fixed; 
    top: 0;
    left: 0;
    width: 100%;
    background-color: #f0f0f0; 
    padding: 1rem;
    /* opacity: 0; */
}
</style>
<style>
.v-row {
  width: 100%;
}
</style>
