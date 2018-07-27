import { Component, ViewChild, OnInit } from '@angular/core';
import { myDialogComponent } from './shared/dialog/dialog.component';
import { JWTService } from './shared/rest/jwt.service';
import { SettingsService } from './shared/settings/settings.service';

@Component({
  selector: 'ttf-root',
  templateUrl: './app.component.html'
})
export class AppComponent implements OnInit {
    title = 'app';

    @ViewChild('renewLoginDialog') loginDialog: myDialogComponent;
    private password: string;

    style: any;

    constructor(private jwt: JWTService, private settings: SettingsService) {}

    ngOnInit(): void {
        this.jwt.sessionExpiry.subscribe(() => {
            this.loginDialog.open();
        });
        this.settings.getSetting('theme').subscribe(theme => {
            this.style = theme;
            if (theme != null) {
                for (const   name in theme) {
                    if (name === 'name') { continue; }
                    if (theme.hasOwnProperty(name)) {
                        this.setColor(name, theme[name]);
                    }
                }
            }
        });
    }

    private setColor(name: string, color: string) {
        if (color == null) {
            document.documentElement.style.removeProperty(`--${name}`);
        } else {
            document.documentElement.style.setProperty(`--${name}`, color);
        }
    }

    renewLogin = () => {
        if (!this.jwt.tokenIsFresh) {
            this.jwt.freshLogin(this.password);
        }
    }
}
