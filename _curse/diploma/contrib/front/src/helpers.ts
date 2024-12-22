import { UnnecessaryEventEmitter } from "./eventBus";
import { Config } from "./settings";


export type Method = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

async function refreshTokens() {
    await fetch(`${Config.backend_address}/auth/refresh/`, {method: 'POST'});
}

export async function getWebsocket(url: string) {
    let result;
    try {
        result = new WebSocket(url);
    } catch {
        await refreshTokens();
        try {
            result = new WebSocket(url);
        } catch {
            UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
                title: 'WebSocket сервер недоступен',
                text: undefined,
                severity: 'warning'
            })
        }
    }
    return result;
}

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
        await refreshTokens();
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
            UnnecessaryEventEmitter.emit(Config.alertMessageKey, {
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

export async function fetchPersonalInfo(auto_error: boolean = true) {
    const userInfoResponse = await fetch_data(
        `${Config.backend_address}/users/me/`,
        'GET',
        undefined,
        false
    )
    if (!userInfoResponse) {
        if (auto_error) await logout();
        return false;
    }
    localStorage.setItem(Config.userInfoProperty, JSON.stringify(userInfoResponse.data.user));
    return true;
}