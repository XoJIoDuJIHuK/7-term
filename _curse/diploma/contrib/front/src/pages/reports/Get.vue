<template>
    <v-container>
        <v-row>
            <v-col>{{ report.reason_text }}</v-col>
            <v-col>{{ (new Date(report.created_at)).toLocaleString() }}</v-col>
            <v-col>{{ report.status }}</v-col>
        </v-row>
        <v-row>
            {{ report.text }}
        </v-row>
        <v-row>
            <v-container>
                <v-row v-if="comments.length === 0">No comments</v-row>
                <v-row v-for="comment in comments" :class="`comment ${currentUserId == comment.sender_id ? 'mine' : 'others'}`">
                    <v-col style="max-width: 10vw;">{{ comment.sender_name }}</v-col>
                    <v-col>
                        <v-container>
                            <v-row>{{ comment.text }}</v-row>
                            <v-row>
                                <v-col>{{ (new Date(comment.created_at)).toLocaleString() }}</v-col>
                            </v-row>
                        </v-container>
                    </v-col>
                </v-row>
                <v-row>
                    <v-col>
                        <v-text-field v-model="commentText" label="Comment"></v-text-field>
                    </v-col>
                    <v-col>
                        <v-btn variant="elevated" color="info" @click="sendComment">
                            <v-icon icon="mdi-send"></v-icon>
                        </v-btn>
                    </v-col>
                </v-row>
            </v-container>
        </v-row>
    </v-container>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router';
import { fetch_data } from '../../helpers';
import { Config } from '../../settings';

const comments = ref([]);
const commentText = ref('');
const report = reactive({
    text: '',
    reason_text: '',
    status: '',
    created_at: new Date(),
    closed_at: null,
    closed_by_user_name: null
});
const route = useRoute();
const router = useRouter();
const socket = ref(null);

const currentUserId = ref(null);

onMounted(async () => {
    currentUserId.value = JSON.parse(localStorage.userInfo).id;
    let response = await fetch_data(`${Config.backend_address}/articles/${route.params.article_id}/report/`)
    if (!response) router.push('/error')
    else Object.assign(report, response.data.report)

    response = await fetch_data(`${Config.backend_address}/articles/${route.params.article_id}/report/comments/`)
    if (!response) comments.value = [];
    else comments.value = response.data.list;

    socket.value = new WebSocket(`${Config.websocket_address}/articles/${route.params.article_id}/report/comments/ws/`)
    socket.value.addEventListener('message', event => {
        console.log(JSON.parse(event.data))
        comments.value.push(JSON.parse(event.data))
    })
})

async function sendComment() {
    const response = await fetch_data(
        `${Config.backend_address}/articles/${route.params.article_id}/report/comments/`,
        'POST',
        JSON.stringify({
            text: commentText.value
        }),
    )
    if (response) {
        commentText.value = '';
        comments.value.push(response.data.comment)
    }
}

</script>

<style scoped>
.comment {
    margin-bottom: 8px;
    padding: 4px;
    border-radius: 8px;
}

.comment.mine {
    background-color: rgb(182, 182, 255);
}

.comment.others {
    background-color: rgb(164, 229, 164);
}
</style>