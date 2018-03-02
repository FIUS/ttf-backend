import { Injectable } from '@angular/core';

@Injectable()
export class JWTService {

    readonly TOKEN = 'token';
    readonly REFRESH_TOKEN = 'refresh_token';

    updateTokens(loginToken: string, refreshToken?: string) {
        localStorage.setItem(this.TOKEN, loginToken);
        if (refreshToken != null) {
            localStorage.setItem(this.REFRESH_TOKEN, refreshToken);
        }
    }

    logout() {
        localStorage.removeItem(this.TOKEN);
        localStorage.removeItem(this.REFRESH_TOKEN);
    }

    token() {
        return localStorage.getItem(this.TOKEN);
    }

    refreshToken() {
        return localStorage.getItem(this.REFRESH_TOKEN);
    }

    private tokenToJson(token: string) {
        return JSON.parse(atob(this.token().split('.')[1]));
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

    isModerator() {
        const token = this.token();
        return (token != null) && (this.tokenToJson(token).user_claims > 0);
    }

    isAdmin() {
        const token = this.token();
        return (token != null) && (this.tokenToJson(token).user_claims > 1);
    }

}
