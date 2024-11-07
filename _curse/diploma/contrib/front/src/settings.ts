import { reactive } from 'vue'

export const Config = {
    backend_address: 'http://localhost:8000/api',
    websocket_address: 'ws://localhost:8000/api',
}

export const store = reactive({
    languages: {
        items: [],
        getValue: function (index: number | null) { return index === null ? null : this.items[index] },
        getSelectItems: function(): {value: number, title: string}[] {
            return this.items.map((value) => ({
                value: parseInt(value.id, 10),
                title: value.name,
            }));
        }
    },
    models: {
        items: [],
        getValue: function (index: number | null) { return index === null ? null : this.items[index] },
        getSelectItems: function(): {value: number, title: string}[] {
            return this.items.map((value) => ({
                value: parseInt(value.id, 10),
                title: `${value.provider} ${value.name}`,
            }));
        }
    },
    prompts: {
        items: [],
        getValue: function (index: number | null) { return index === null ? null : this.items[index] },
        getSelectItems: function(): {value: number, title: string}[] {
            return this.items.map((value) => ({
                value: parseInt(value.id, 10),
                title: value.title,
            }));
        }
    },
    reportReasons: {
        items: [],
        getValue: function (index: number | null) { return index === null ? null : this.items[index] },
        getSelectItems: function(): {value: number, title: string}[] {
            return this.items.map((value) => ({
                value: parseInt(value.id, 10),
                title: value.text,
            }));
        }
    }
})

export const userRoles = {
    guest: 'Гость',
    user: 'Пользователь',
    mod: 'Модератор',
    admin: 'Администратор',
}