export type AlertSeverity = 'info' | 'warning' | 'error' | 'success'

export type AlertMessageParams = {
    title: string,
    text: string,
    severity: AlertSeverity
}

export const UnnecessaryEventEmitter = {
    events: {} as Record<string, Array<(params: any) => void>>,
    on: function(event: string, handler: (params: any) => void) {
        if (!this.events[event]) {
            this.events[event] = []
        }
        this.events[event].push(handler)
    },
    emit: function(event: string, params: any) {
        if (!this.events[event]) return
        for (let handler of this.events[event]) {
            handler(params)
        }
    },
}