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
    const getResult = () => {
        return fetch(
            address, {
                method: method,
                body: data,
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );
    }
    let response = await getResult();
    if (response.status === 401) {
        await fetch(`${Config.backend_address}/auth/refresh/`, {method: 'POST'});
        response = await getResult();
        if (response.status === 401) {
            await logout();
            location.href = '/';
            return;
        }
    }
    if (!response.ok) {
        const e = await response.json()
        if (alertError) {
            let errorText = e.message
            if (response.status === 422) {
                errorText = `Ошибка валидации: ${e.errors[0].loc.join(', ')}. ${e.errors[0].msg}`
            } else if (response.status === 413) {
                errorText = `Превышен максимально допустимый размер`
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

export async function fetchPersonalInfo() {
    const userInfoResponse = await fetch_data(`${Config.backend_address}/users/me/`)
    if (!userInfoResponse) {
        await logout()
        return
    }
    localStorage.setItem(Config.userInfoProperty, JSON.stringify(userInfoResponse.data.user));
}