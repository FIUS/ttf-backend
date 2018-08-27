import { Injectable } from '@angular/core';
import { Subject } from 'rxjs/Rx';

export class Message {

    readonly type: string;
    readonly title?: string;
    readonly message: string;
    readonly timeout?: number;
    readonly createdAt: Date;

    constructor(type: string, message: string, title?: string, timeout?: number) {
        if (type.match(/info|warning|error/) == null) {
            type = 'error';
        }
        this.type = type;
        this.title = title;
        this.message = message;
        this.timeout = timeout;
        this.createdAt = new Date();
    }

}

@Injectable()
export class InfoService {

    private messageSource = new Subject<Message>();

    messages = this.messageSource.asObservable();

    constructor() {}

    emitInfo(message: string, title?: string, timeout?: number) {
        const defaultTimeout = (window as any).infoTimeout || 5000;
        this.messageSource.next(new Message('info', message, title, timeout != null ? timeout : defaultTimeout));
    }

    emitWarning(message: string, title?: string, timeout?: number) {
        const defaultTimeout = (window as any).alertTimeout || 15000;
        this.messageSource.next(new Message('warning', message, title, timeout != null ? timeout : defaultTimeout));
    }

    emitError(message: string, title?: string, timeout?: number) {
        const defaultTimeout = (window as any).errorTimeout || -1;
        this.messageSource.next(new Message('error', message, title, timeout != null ? timeout : defaultTimeout));
    }

}
