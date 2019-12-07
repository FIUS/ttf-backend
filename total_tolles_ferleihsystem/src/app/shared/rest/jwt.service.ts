
import {timer as observableTimer,  Observable, Subject, BehaviorSubject, } from 'rxjs';

import {filter, take} from 'rxjs/operators';
import { Injectable, OnInit, Injector } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from './api.service';


@Injectable()
export class JWTService implements OnInit {

    private sessionExpirySource = new Subject<boolean>();
    readonly sessionExpiry = this.sessionExpirySource.asObservable();

    private apiTokenSource = new BehaviorSubject<string>(null);

    private userSource = new BehaviorSubject<string>(undefined);
    readonly user = this.userSource.asObservable();

    readonly TOKEN = 'ttf_token';
    readonly REFRESH_TOKEN = 'ttf_refresh_token';

    private api: ApiService;


    constructor (private injector: Injector, private router: Router) {
        observableTimer(1).pipe(take(1)).subscribe((() => {
            this.ngOnInit()
        }).bind(this))
    }

    ngOnInit(): void {
        this.api = this.injector.get(ApiService);
        observableTimer(1, 60000).subscribe((() => {
            if (this.loggedIn()) {
                this.userSource.next(this.username());
                let future = new Date();
                future = new Date(future.getTime() + (3 * 60 * 1000))
                if (this.expiration(this.token()) < future) {
                    this.api.refreshLogin(this.refreshToken());
                } else {
                    this.apiTokenSource.next(this.token());
                }
                if (this.expiration(this.refreshToken()) < future) {
                    this.sessionExpirySource.next(true);
                    this.apiTokenSource = new BehaviorSubject<string>(null);
                }
            }
        }).bind(this));
        if (!this.loggedIn()) {
            this.userSource.next(undefined);
            this.apiTokenSource = new BehaviorSubject<string>(null);
            this.api.guestLogin();
        }
    }

    updateTokens(loginToken: string, refreshToken?: string) {
        localStorage.setItem(this.TOKEN, loginToken);
        this.apiTokenSource.next(loginToken);
        if (refreshToken != null) {
            localStorage.setItem(this.REFRESH_TOKEN, refreshToken);
        }
        if (this.router.url === '/login' && this.loggedIn()) {
            this.router.navigate(['/']);
        }
        if (this.userSource.value !== this.username()) {
            this.userSource.next(this.username());
        }
    }

    logout() {
        this.userSource.next(undefined);
        this.apiTokenSource = new BehaviorSubject<string>(null);
        localStorage.removeItem(this.TOKEN);
        localStorage.removeItem(this.REFRESH_TOKEN);
        this.api.guestLogin();
        this.router.navigate(['/login']);
    }

    freshLogin(password: string) {
        this.api.freshLogin(password);
    }

    token() {
        return localStorage.getItem(this.TOKEN);
    }

    refreshToken() {
        return localStorage.getItem(this.REFRESH_TOKEN);
    }

    getValidApiToken() {
        return this.apiTokenSource.asObservable().pipe(filter(token => {
            if (token == null) { //filter out null
                return false;
            }
            // filter out expired tokens
            let future = new Date();
            future = new Date(future.getTime() + (60 * 1000))
            if (this.expiration(this.token()) < future) {
                return false;
            }
            return true;
        }),take(1),);
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
        return (token != null) && (this.tokenToJson(token).user_claims === 1);
    }

    isModerator() {
        const token = this.token();
        return (token != null) && (this.tokenToJson(token).user_claims > 1);
    }

    isAdmin() {
        const token = this.token();
        return (token != null) && (this.tokenToJson(token).user_claims > 2);
    }

}
