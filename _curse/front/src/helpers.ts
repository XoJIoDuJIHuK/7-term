type Method = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export async function fetch_data(
    address: string,
    method: Method,
    data: any
) {
    const access_token = localStorage.getItem('access_token')
    const refresh_token = localStorage.getItem('access_token')
    let headers = {}
    if (access_token) {
        headers = {
            'Authorization': `Bearer ${access_token}`
        }
    }
    return await fetch(
        address, {
            method: method,
            body: data,
            headers: headers
        }
    )
    .then(d => d.json())
    .catch(e => {
        console.log('ERROR')
        console.error(e)
    })
}