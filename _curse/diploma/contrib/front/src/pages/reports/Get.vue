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
        <v-row v-if="userRole == Config.userRoles.mod">
            <v-col>
                <div v-html="renderedSourceMarkdown" class="markdown-renderer"></div>
            </v-col>
            <v-col>
                <div v-html="renderedTranslatedMarkdown" class="markdown-renderer"></div>
            </v-col>
        </v-row>
        <v-row v-if="userRole == Config.userRoles.mod && report.status === Config.reportStatuses.open">
            <v-col><v-btn color="success" @click="updateStatus(Config.reportStatuses.satisfied)">Удовлетворить</v-btn></v-col>
            <v-col><v-btn color="error" @click="updateStatus(Config.reportStatuses.rejected)">Отклонить</v-btn></v-col>
        </v-row>
        <v-row v-else-if="report.status === Config.reportStatuses.open">
            <v-col><v-btn color="error" @click="updateStatus(Config.reportStatuses.closedByUser)">Закрыть</v-btn></v-col>
        </v-row>
        <v-row>
            <v-container>
                <v-row v-if="comments.length === 0" justify="center" class="text--disabled">Комментариев нет</v-row>
                <v-row
                    v-for="comment in comments"
                    :key="comment.id"
                    :class="['comment', { mine: currentUserId === comment.sender_id, others: currentUserId !== comment.sender_id }]"
                >
                    <v-col cols="auto" class="pr-4">
                        {{ comment.sender_name }}
                    </v-col>
                    <v-col>
                        <v-container>
                            <v-row>
                                {{ comment.text }}
                            </v-row>
                            <v-row class="text--secondary">
                                {{ (new Date(comment.created_at)).toLocaleString() }}
                            </v-row>
                        </v-container>
                    </v-col>
                </v-row>
                <v-row v-if="report.status === Config.reportStatuses.open">
                    <v-col cols="8">
                        <v-text-field v-model="commentText" label="Комментарий" />
                    </v-col>
                    <v-col cols="4">
                        <v-btn variant="elevated" color="info" @click="sendComment">
                            <v-icon icon="mdi-send" />
                        </v-btn>
                    </v-col>
                </v-row>
            </v-container>
        </v-row>
    </v-container>
</template>

<script setup lang="ts">
import { onMounted, reactive, Ref, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router';
import {fetch_data, getWebsocket} from '../../helpers';
import { Config } from '../../settings';
import { UnnecessaryEventEmitter } from '../../eventBus';
import {marked} from "marked";

const comments: Ref<Array<any>> = ref([]);
const commentText = ref('');
const report = reactive({
    text: '',
    reason_text: '',
    status: '',
    created_at: new Date(),
    closed_at: null,
    closed_by_user_name: null,
    source_text: '',
    source_language_id: null,
    translated_text: '',
    translated_language_id: null
});
const route = useRoute();
const router = useRouter();
const socket: Ref<WebSocket | null> = ref(null);
const renderedSourceMarkdown = ref('');
const renderedTranslatedMarkdown = ref('');

const currentUserId = ref(null);
const userRole = JSON.parse(localStorage.getItem(Config.userInfoProperty) as string).role

onMounted(async () => {
    currentUserId.value = JSON.parse(localStorage.userInfo).id;
    let response = await fetch_data(`${Config.backend_address}/articles/${route.params.article_id}/report/`)
    if (!response) await router.push('/error')
    else Object.assign(report, response.data.report)
    renderedSourceMarkdown.value = await marked(report.source_text);
    renderedTranslatedMarkdown.value = await marked(report.translated_text);

    response = await fetch_data(`${Config.backend_address}/articles/${route.params.article_id}/report/comments/`)
    comments.value = response ? response.data.list : [];

    const connectedSocket = await getWebsocket(`${Config.websocket_address}/articles/${route.params.article_id}/report/comments/ws/`);
    if (!connectedSocket) return;
    socket.value = connectedSocket;
    socket.value.addEventListener('message', event => {
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
        // comments.value.push(response.data.comment)
    }
}

async function updateStatus(newStatus: string) {
    const response = await fetch_data(
        `${Config.backend_address}/articles/${route.params.article_id}/report/status/?new_status=${newStatus}`,
        'PATCH',
    )
    if (response) {
        UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
            title: 'Жалоба создана',
            text: undefined,
            severity: 'info'
        });
        report.status = newStatus;
    }
}

</script>

<style scoped>
.comment {
    margin-bottom: 8px;
    padding: 4px;
    border-radius: 8px;
    box-shadow: 0 0 4px rgba(0, 0, 0, 0.1);
}

.comment.mine {
    background-color: rgb(182, 182, 255);
    border-left: 4px solid rgb(100, 100, 255);
}

.comment.others {
    background-color: rgb(164, 229, 164);
    border-right: 4px solid rgb(100, 255, 100);
}

.comment .v-col {
    padding: 0;
}

.comment .v-col:first-child {
    font-weight: bold;
}

.comment .v-container {
    padding: 5px;
}

.comment .v-row {
    margin-bottom: 4px;
}

.comment .v-row:last-child {
    margin-bottom: 0;
}

.comment .v-text-field {
    padding: 0;
    margin-bottom: 4px;
}

.comment .v-btn {
    margin-left: 8px;
}
</style>