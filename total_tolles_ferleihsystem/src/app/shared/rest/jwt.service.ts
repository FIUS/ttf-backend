import { Injectable, OnInit, Injector } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from './api.service';
import { Observable, } from 'rxjs/Rx';


@Injectable()
export class JWTService implements OnInit {

    readonly TOKEN = 'token';
    readonly REFRESH_TOKEN = 'refresh_token';

    private api: ApiService;

    constructor (private injector: Injector, private router: Router) {
        Observable.timer(1).take(1).subscribe((() => {
            this.ngOnInit()
        }).bind(this))
    }

    ngOnInit(): void {
        this.api = this.injector.get(ApiService);
        Observable.timer(1, 60000).subscribe((() => {
            if (this.loggedIn()) {
                let future = new Date();
                future = new Date(future.getTime() + (3 * 60 * 1000))
                if (this.expiration(this.token()) < future) {
                    this.api.refreshLogin(this.refreshToken());
                }
            }
        }).bind(this));
        if (!this.loggedIn()) {
            this.api.guestLogin();
        }
    }

    updateTokens(loginToken: string, refreshToken?: string) {
        localStorage.setItem(this.TOKEN, loginToken);
        if (refreshToken != null) {
            localStorage.setItem(this.REFRESH_TOKEN, refreshToken);
        }
        if (this.router.url === '/login' && this.loggedIn()) {
            this.router.navigate(['/']);
        }
    }

    logout() {
        localStorage.removeItem(this.TOKEN);
        localStorage.removeItem(this.REFRESH_TOKEN);
        this.api.guestLogin();
        this.router.navigate(['/login']);
    }

    token() {
        return localStorage.getItem(this.TOKEN);
    }

    refreshToken() {
        return localStorage.getItem(this.REFRESH_TOKEN);
    }

    private tokenToJson(token: string) {
        return JSON.parse(atob(token.split('.')[1]));
    }

    private expiration(token: string): Date {
        const decoded = this.tokenToJson(token);
        const exp = new Date(0);
        exp.setUTCSeconds(decoded.exp);
        return exp;
    }

    loggedIn() {
        const token = this.refreshToken();
        return (token != null) && (this.expiration(token) > new Date());
    }

    tokenIsActive() {
        const token = this.token();
        return (token != null) && (this.expiration(token) > new Date());
    }

    tokenIsFresh() {
        const token = this.token();
        return (token != null) && !(!this.tokenToJson(token).fresh);
    }

    username() {
        const token = this.token();
        if (token == null) {
            return undefined;
        }
        return this.tokenToJson(token).identity;
    }

    isUser() {
        const token = this.token();
        return (token != null) && (this.tokenToJson(token).user_claims === 0);
    }

    isModerator() {
        const token = this.token();
        return (token != null) && (this.tokenToJson(token).user_claims > 0);
    }

    isAdmin() {
        const token = this.token();
        return (token != null) && (this.tokenToJson(token).user_claims > 1);
    }

}
