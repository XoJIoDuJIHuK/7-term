<template>
    <header>
        <nav>
            <v-container>
                <v-row>
                    <v-col v-if="userRole === Config.userRoles.user">
                        <router-link to="/articles">
                            <v-btn class="mr-4" variant="outlined">Articles</v-btn>
                        </router-link>
                        <router-link to="/configs">
                            <v-btn class="mr-4" variant="outlined">Configs</v-btn>
                        </router-link>
                    </v-col>
                    <v-col v-else-if="userRole === Config.userRoles.mod">
                        <router-link to="/reports">
                            <v-btn class="mr-4" variant="outlined">Reports</v-btn>
                        </router-link>
                    </v-col>
                    <v-col v-if="userRole === Config.userRoles.admin">
                        <router-link to="/users">
                            <v-btn class="mr-4" variant="outlined">Users</v-btn>
                        </router-link>
                        <router-link to="/analytics">
                            <v-btn class="mr-4" variant="outlined">Analytics</v-btn>
                        </router-link>
                        <router-link to="/prompts">
                            <v-btn class="mr-4" variant="outlined">Prompts</v-btn>
                        </router-link>
                        <router-link to="/models">
                            <v-btn class="mr-4" variant="outlined">Models</v-btn>
                        </router-link>
                    </v-col>
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
import { Config } from '../settings';

const userRole = JSON.parse(localStorage.getItem(Config.userInfoProperty) as string).role;
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
