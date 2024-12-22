<template>
    <v-container>
        <v-card>
            <v-card-title>
                <h2>Подтвердите смену пароля</h2>
            </v-card-title>
            <v-card-text>
                <v-form>
                    <v-text-field
                        v-model="newPassword"
                        label="Новый пароль"
                        :rules="[rules.required]"
                        type="password"
                        required
                    ></v-text-field>
                    <v-text-field
                        v-model="confirmPassword"
                        label="Подтвердите пароль"
                        :rules="[rules.required, rules.passwordsMatch]"
                        type="password"
                        required
                    ></v-text-field>
                </v-form>
            </v-card-text>
            <v-card-actions>
                <v-btn color="primary" @click="submit">Подтвердить</v-btn>
                <v-btn @click="cancel">Отмена</v-btn>
            </v-card-actions>
        </v-card>
    </v-container>
</template>


<script setup lang="ts">
import { fetch_data } from '../helpers';
import { useRoute, useRouter } from 'vue-router';
import {onMounted, ref} from 'vue';
import { Config } from '../settings';
import {UnnecessaryEventEmitter} from "../eventBus.ts";

const isLoading = ref(true);
const newPassword = ref('');
const confirmPassword = ref('');
const route = useRoute();
const router = useRouter();
const code = route.query.code;

const rules = {
    required: (v: string | undefined) => !!v || 'Введите пароль',
    passwordsMatch: () => confirmPassword.value === newPassword.value || 'Пароли не совпадают'
}

onMounted(async () => {
    if (!code) {
        UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
            title: 'Не предоставлен код сброса пароля',
            text: undefined,
            severity: 'error'
        });
        await router.push('/');
    }
})

async function submit() {
    if (newPassword.value !== confirmPassword.value) {
        UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
            title: undefined,
            text: 'Пароли не совпадают',
            severity: 'warning'
        })
        return;
    }
    isLoading.value = true;
    const response = await fetch_data(
        `${Config.backend_address}/auth/restore-password/confirm/`,
        'PATCH',
        JSON.stringify({
            new_password: newPassword.value,
            code,
        })
    );
    isLoading.value = false;
    if (!response) return;
    UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
        title: 'Пароль успешно изменён',
        text: undefined,
        severity: 'success'
    })
    await router.push('/');
}

async function cancel() { await router.push('/'); }
</script>