import { UnnecessaryEventEmitter } from "./eventBus";
import { Config } from "./settings";


export type Method = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export async function fetch_data(
    address: string,
    method: Method = 'GET',
    data: any = undefined,
    alertError: boolean = true,
    throwError: boolean = false,
) {
    const response = await fetch(
        address, {
            method: method,
            body: data,
            headers: {
                'Content-Type': 'application/json'
            }
        }
    )
    if (!response.ok) {
        const e = await response.json()
        if (alertError) {
            let errorText = e.message
            if (response.status === 422) {
                errorText = `Ошибка валидации: ${e.errors[0].loc.join(', ')}. ${e.errors[0].msg}`
            }
            UnnecessaryEventEmitter.emit('AlertMessage', {
                title: `${response.status} ${response.statusText}`,
                text: errorText,
                severity: 'error'
            })
        }
        if (throwError) {
            throw e.message
        }
        return undefined
    }
    return response.json()
}

export async function logout() {
    await fetch_data(`${Config.backend_address}/auth/logout/`)
    localStorage.removeItem(Config.userInfoProperty);
    location.href = '/';
}