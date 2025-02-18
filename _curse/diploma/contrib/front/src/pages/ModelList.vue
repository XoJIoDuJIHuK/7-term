<template>
    <v-data-table :items="users" :headers="headers">
        <template v-slot:top>
            <v-toolbar
                flat
            >
                <v-toolbar-title>Модели</v-toolbar-title>
                <v-divider
                class="mx-4"
                inset
                vertical
                ></v-divider>

                <v-spacer></v-spacer>

                <v-dialog
                    v-model="dialog"
                    max-width="500px"
                >
                    <template v-slot:activator="{ props }">
                        <v-btn
                            class="mb-2"
                            color="primary"
                            dark
                            v-bind="props"
                        >Создать</v-btn>
                    </template>
                    <v-card>
                        <v-card-title><span class="text-h5">{{ formTitle }}</span></v-card-title>

                        <v-card-text>
                            <v-container>
                                <v-row>
                                  <v-col
                                      cols="12"
                                      md="4"
                                      sm="6"
                                  >
                                    <v-text-field
                                        v-model="editedItem.show_name"
                                        :rules="[rules.required, rules.maxLength(50)]"
                                        label="Отображаемое название"
                                    ></v-text-field>
                                  </v-col>
                                  <v-col
                                      cols="12"
                                      md="4"
                                      sm="6"
                                  >
                                      <v-text-field
                                          v-model="editedItem.name"
                                          label="Название"
                                      ></v-text-field>
                                  </v-col>
                                  <v-col
                                      cols="12"
                                      md="4"
                                      sm="6"
                                  >
                                      <v-text-field
                                          v-model="editedItem.provider"
                                          label="Провайдер"
                                      ></v-text-field>
                                  </v-col>
                                </v-row>
                            </v-container>
                        </v-card-text>

                        <v-card-actions>
                            <v-spacer></v-spacer>
                            <v-btn
                                color="blue-darken-1"
                                variant="text"
                                @click="close"
                            >Отмена</v-btn>
                            <v-btn
                                :loading="editButtonLoading"
                                color="blue-darken-1"
                                variant="text"
                                @click="save"
                            >Сохранить</v-btn>
                        </v-card-actions>
                    </v-card>
                </v-dialog>
            </v-toolbar>
        </template>
        <template v-slot:item.actions="{ item }">
            <v-icon
                class="me-2"
                size="small"
                @click="editItem(item)"
            >mdi-pencil</v-icon>
            <v-icon
                size="small"
                @click="deleteItem(item)"
            >{{ deleteButtonLoading ? 'mdi-loading' : 'mdi-delete' }}</v-icon>
        </template>
    </v-data-table>
</template>

<script setup lang="ts">
import { fetch_data } from '../helpers';
import { computed, onMounted, reactive, ref, Ref } from 'vue';
import { Config, DataTableHeader, validationRules as rules } from '../settings';
import { Method } from '../helpers';
import { UnnecessaryEventEmitter } from '../eventBus';

type Model = {
    id: string;
    show_name: string;
    name: string;
    provider: string;
    created_at: string;
}

const users: Ref<Model[]> = ref([]);
const editedIndex = ref(-1);
const dialog = ref(false);
const dialogDelete = ref(false);
const formTitle = ref('Новая модель');
const editButtonLoading = ref(false);
const deleteButtonLoading = ref(false);
const editedItem = reactive({
    id: '',
    show_name: '',
    name: '',
    provider: '',
})
const defaultItem = Object.assign({}, editedItem);

const headers = computed<DataTableHeader[]>(() => {
    const rawHeaders = [
        { title: 'ID', sortable: false, key: 'id', },
        { title: 'Отображаемое название', key: 'show_name' },
        { title: 'Название', key: 'name' },
        { title: 'Провайдер', key: 'provider' },
        { title: 'Дата создания', key: 'created_at' },
        { title: 'Действия', key: 'actions', sortable: false },
    ];
    // @ts-ignore
    const headers: DataTableHeader[] = rawHeaders.map(e => {
        const baseHeader = {
            key: '',
            title: '',
            align: 'start',
            sortable: true,
            width: undefined,
        };
        Object.assign(baseHeader, e);
        return baseHeader;
    });

    return headers;
});

onMounted(async () => {
    const response = await fetch_data(`${Config.backend_address}/models/admin/`);
    if (!response) return
    users.value = response.data.list;
})

async function editItem (item: Model) {
    editedIndex.value = users.value.indexOf(item)
    Object.assign(editedItem, item)
    dialog.value = true
}

async function deleteItem(item: Model) {
    const response = await fetch_data(
        `${Config.backend_address}/models/${item.id}/`,
        'DELETE'
    )
    if (response) {
        UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
            title: 'Промпт удалён',
            text: undefined,
            severity: 'success'
        })
        dialogDelete.value = true;
        location.reload();
    }
}

async function close() {
    dialog.value = false
    Object.assign(editedItem, defaultItem)
    editedIndex.value = -1
}

async function save() {
    editButtonLoading.value = true
    let url = `${Config.backend_address}/models/`;
    let method = 'POST';
    if (editedIndex.value > -1) {
        url += `${editedItem.id}/`;
        method = 'PUT';
    }
    const response = await fetch_data(
        url,
        method as Method,
        JSON.stringify(editedItem)
    )
    editButtonLoading.value = false;
    if (response) {
        UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
            title: 'Модель сохранена',
            text: undefined,
            severity: 'success'
        })
        location.reload();
    }
}
</script>