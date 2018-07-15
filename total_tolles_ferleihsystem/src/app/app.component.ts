import { Component, ViewChild } from '@angular/core';
import { myDialogComponent } from './shared/dialog/dialog.component';
import { JWTService } from './shared/rest/jwt.service';

@Component({
  selector: 'ttf-root',
  templateUrl: './app.component.html'
})
export class AppComponent {
    title = 'app';

    @ViewChild('renewLoginDialog') loginDialog: myDialogComponent;
    private password: string;

    constructor(private jwt: JWTService) {
        jwt.sessionExpiry.subscribe(() => {
            this.loginDialog.open();
        });
    }

    renewLogin = () => {
        if (!this.jwt.tokenIsFresh) {
            this.jwt.freshLogin(this.password);
        }
    }
}
