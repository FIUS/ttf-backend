import { Injectable, Injector } from '@angular/core';
import { Subject, Observable } from 'rxjs/Rx';
import { list } from 'postcss';
import { SettingsService } from '../settings/settings.service';

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

    private settings: SettingsService;

    private messageSource = new Subject<Message>();

    messages = this.messageSource.asObservable();

    constructor(private injector: Injector) {
        Observable.timer(1000).take(1).subscribe((() => {
            this.ngOnInit();
        }).bind(this))
    }

    ngOnInit(): void {
        //this.settings = this.injector.get(SettingsService);
    }

    emitInfo(message: string, title?: string, timeout?: number) {
        if (this.settings == null) {
            this.messageSource.next(new Message('info', message, title, timeout != null ? timeout : 5000));
        }
        this.settings.getSetting('infoTimeout').subscribe(defaultTimeout => {
            if (defaultTimeout == null) {
                defaultTimeout = 5000;
            }
            this.messageSource.next(new Message('info', message, title, timeout != null ? timeout : defaultTimeout));
        });
    }

    emitWarning(message: string, title?: string, timeout?: number) {
        if (this.settings == null) {
            this.messageSource.next(new Message('info', message, title, timeout != null ? timeout : 15000));
        }
        this.settings.getSetting('alertTimeout').subscribe(defaultTimeout => {
            if (defaultTimeout == null) {
                defaultTimeout = 15000;
            }
            this.messageSource.next(new Message('warning', message, title, timeout != null ? timeout : defaultTimeout));
        });
    }

    emitError(message: string, title?: string, timeout?: number) {
        if (this.settings == null) {
            this.messageSource.next(new Message('info', message, title, timeout != null ? timeout : -1));
        }
        this.settings.getSetting('alertTimeout').subscribe(defaultTimeout => {
            if (defaultTimeout == null) {
                defaultTimeout = -1;
            }
            this.messageSource.next(new Message('error', message, title, timeout != null ? timeout : defaultTimeout));
        });
    }

}
