import { UnnecessaryEventEmitter } from "./eventBus";
import { Config } from "./settings";
import { Router } from "vue-router";


type Method = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export async function fetch_data(
    address: string,
    method: Method = 'GET',
    data: any = undefined,
    alertError: boolean = true,
    throwError: boolean = false,
) {
    // const access_token = localStorage.getItem('access_token')
    const access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2luZm8iOnsiaWQiOiIxOTVlOTgwMS02MzJmLTQ3MGQtYjFiNi01MWFhMGVlYjk0MTkiLCJyb2xlIjoiXHUwNDFmXHUwNDNlXHUwNDNiXHUwNDRjXHUwNDM3XHUwNDNlXHUwNDMyXHUwNDMwXHUwNDQyXHUwNDM1XHUwNDNiXHUwNDRjIn0sImV4cCI6MTczNDEzNjU1MS40MTEzMTY2fQ.CIjop4h2VtfS2MZmklz_r05Bz-xGrg9jtH6fCQT2sgM'
    // const refresh_token = localStorage.getItem('access_token')
    const headers = new Headers()
    headers.append('Content-Type', 'application/json')
    if (access_token) {
        headers.append('Authorization', `Bearer ${access_token}`)
    }
    const response = await fetch(
        address, {
            method: method,
            body: data,
            headers: headers
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

export async function logout(router: Router) {
    await fetch_data(`${Config.backend_address}/auth/logout/`)
    localStorage.removeItem('userInfo');
    router.push('/')
}