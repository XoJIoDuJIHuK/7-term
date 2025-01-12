import { reactive } from 'vue'

export const Config = {
    // backend_address: 'https://ugabuntu.com/api',
    // websocket_address: 'wss://ugabuntu.com/api',
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
    alertMessageKey: 'AlertMessage',
}

export type Language = {
    id: number,
    name: string,
    iso_code: string
}
export type Model = {
    id: number,
    show_name: string,
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

export type StoreKeys = 'languages' | 'models' | 'prompts' | 'reportReasons'

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
                title: value.show_name,
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

export const validationRules = {
    required: (v: string | undefined) => !!v || 'Обязательное поле',
    email: (value: string) => {
        const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
        return pattern.test(value) || 'Неправильный адрес электронной почты.'
    },
    maxLength: (maxLength: number) => (value: string) => value.length <= maxLength || `Превышена длина: ${maxLength}`
}

export interface DataTableHeader {
    key: string
    title: string
    align?: 'start' | 'end' | 'center'
    sortable?: boolean
    width?: string | number
}