import { reactive } from 'vue'

export const Config = {
    backend_address: 'http://localhost:8000/api',
    websocket_address: 'ws://localhost:8000/api',
    userRoles: {
        guest: 'Гость',
        user: 'Пользователь',
        mod: 'Модератор',
        admin: 'Администратор',
    },
    reportStatuses: {
        open: 'Открыта',
        closedByUser: 'Закрыта пользователем',
        satisfied: 'Удовлетворена',
        rejected: 'Отклонена',
    },
    userInfoProperty: 'userInfo',
}

export type Language = {
    id: number,
    name: string,
    iso_code: string
}
export type Model = {
    id: number,
    name: string,
    provider: string
}
export type Prompt = {
    id: number,
    title: string
}
export type ReportReason = {
    id: number,
    text: string
}

export const store = reactive({
    languages: {
        items: [] as Array<Language>,
        getValue: function (index: number | null) {
            for (let lang of this.items) {
                if (lang.id === index) {
                    return lang
                }
            }
            return null
        },
        getSelectItems: function(): {value: number, title: string}[] {
            return this.items.map((value) => ({
                value: value.id,
                title: value.name,
            }));
        }
    },
    models: {
        items: [] as Array<Model>,
        getValue: function (index: number | null) {
            for (let lang of this.items) {
                if (lang.id === index) {
                    return lang
                }
            }
            return null
        },
        getSelectItems: function(): {value: number, title: string}[] {
            return this.items.map((value) => ({
                value: value.id,
                title: `${value.provider} ${value.name}`,
            }));
        }
    },
    prompts: {
        items: [] as Array<Prompt>,
        getValue: function (index: number | null) {
            for (let lang of this.items) {
                if (lang.id === index) {
                    return lang
                }
            }
            return null
        },
        getSelectItems: function(): {value: number, title: string}[] {
            return this.items.map((value) => ({
                value: value.id,
                title: value.title,
            }));
        }
    },
    reportReasons: {
        items: [] as Array<ReportReason>,
        getValue: function (index: number | null) {
            for (let lang of this.items) {
                if (lang.id === index) {
                    return lang
                }
            }
            return null
        },
        getSelectItems: function(): {value: number, title: string}[] {
            return this.items.map((value) => ({
                value: value.id,
                title: value.text,
            }));
        }
    }
})