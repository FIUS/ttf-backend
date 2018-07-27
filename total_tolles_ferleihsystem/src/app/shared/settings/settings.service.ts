import { Injectable } from '@angular/core';
import { ApiService } from '../rest/api.service';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { Observable } from 'rxjs/Rx';
import { JWTService } from '../rest/jwt.service';


@Injectable()
export class SettingsService {

    private settingsSource = new BehaviorSubject<{[propName: string]: any}>(new Object());


    constructor(private api: ApiService, private jwt: JWTService) {
        jwt.user.subscribe(username => {
            if (username == null) {
                this.settingsSource.next(new Object());
            } else {
                this.api.getSettings().subscribe(settings => {
                    this.settingsSource.next(JSON.parse(settings));
                });
            }
        })
    }

    getSetting(key: string): Observable<any> {
        return this.settingsSource.map(settings => {
            if (settings != null) {
                return settings[key];
            } else {
                return undefined;
            }
        });
    }

    setSetting(key: string, value: any) {
        this.settingsSource.take(1).subscribe(settings => {
            settings[key] = value;
            const settingsString = JSON.stringify(settings);
            this.settingsSource.next(settings);
            this.api.updateSettings(settingsString).subscribe(settings => {
                this.settingsSource.next(JSON.parse(settings));
            });
        });
    }

}
