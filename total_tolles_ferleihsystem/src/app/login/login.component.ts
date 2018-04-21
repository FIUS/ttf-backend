import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { Router } from '@angular/router';
import { ApiService } from '../shared/rest/api.service';
import { JWTService } from '../shared/rest/jwt.service';
import { timeout } from 'q';

@Component({
  selector: 'ttf-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

    private username: string;
    private password: string = '';

    constructor(private data: NavigationService, private api: ApiService,
        private jwt: JWTService, private router: Router) { }

    ngOnInit(): void {
        if (this.jwt.loggedIn() && !this.jwt.isUser()) {
            this.router.navigate(['/']);
        }
        this.data.changeTitle('Total Tolles Ferleihsystem – Login');
        this.data.changeBreadcrumbs([]);
    }

    credentialsValid(): boolean {
        if (this.username != null && this.username.length >= 3) {
            if (this.password !== undefined && this.password !== null &&
                (this.password.length >= 3 ||
                (this.username === 'Guest' && this.password === ''))) {
                return true;
            }
        }
        return false;
    }

    login() {
        if (this.credentialsValid()) {
            this.api.login(this.username, this.password);
            this.password = '';
        }
    }

    loginAsGuest() {
        this.api.guestLogin();
    }

}
