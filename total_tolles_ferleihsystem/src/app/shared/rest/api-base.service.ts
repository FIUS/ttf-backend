import { Injectable } from '@angular/core';
import { Http, Response, Headers, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Rx';
import { ApiService } from './api.service';

export interface LinkObject {
    readonly href: string;
    readonly templated?: boolean;
}

export interface ApiLinksObject {
    readonly self: LinkObject;
    [propName: string]: LinkObject;
}

export interface ApiObject {
    readonly _links: ApiLinksObject;
    [propName: string]: any;
}

function isApiObject(toTest: any): toTest is ApiObject {
    return '_links' in toTest;
}

function isApiLinksObject(toTest: any): toTest is ApiLinksObject {
    return 'self' in toTest;
}

function isLinkObject(toTest: any): toTest is LinkObject {
    return 'href' in toTest;
}

@Injectable()
export class BaseApiService {

    private runningRequests: Map<string, Observable<ApiObject | ApiObject[]>> = new Map<string, Observable<ApiObject | ApiObject[]>>();

    constructor(private http: Http) {
    }

    private extractUrl(url: string|LinkObject|ApiLinksObject|ApiObject): string {
        if (typeof url === 'string' || url instanceof String) {
            return (url as string);
        }
        if (isApiObject(url)) {
            url = url._links;
        }
        if (isApiLinksObject(url)) {
            url = url.self;
        }
        if (isLinkObject(url)) {
            url = url.href;
        }
        return url;
    }

    private headers(token?: string): RequestOptions {
        const headers = new Headers();
        headers.append('Content-Type', 'application/json');
        if (token != undefined) {
            headers.append('Authorization', 'Bearer ' + token);
        }

        return new RequestOptions({ headers: headers });
    }

    get(url: string|LinkObject|ApiLinksObject|ApiObject, token?: string): Observable<ApiObject | ApiObject[]> {
        url = this.extractUrl(url);
        if (this.runningRequests.has(url)) {
            return this.runningRequests.get(url);
        }
        console.log(url);
        const request = this.http.get(url, this.headers(token))
            .map((res: Response) => {
                this.runningRequests.delete(url as string);
                return res.json();
            }).catch((error: any) => {
                this.runningRequests.delete(url as string);
                return Observable.throw(error.json().error || 'Server error');
            }).publishReplay(1);
        this.runningRequests.set(url, request);
        request.connect();
        return request;
    }

    put(url: string|LinkObject|ApiLinksObject|ApiObject, data, token?: string): Observable<ApiObject> {
        url = this.extractUrl(url);
        return this.http.put(url, JSON.stringify(data), this.headers(token))
            .map((res: Response) => res.json())
            .catch((error: any) => Observable.throw(error.json().error || 'Server error'));
    }

    post(url: string|LinkObject|ApiLinksObject|ApiObject, data, token?: string): Observable<ApiObject> {
        url = this.extractUrl(url);
        return this.http.post(url, JSON.stringify(data), this.headers(token))
            .map((res: Response) => res.json())
            .catch((error: any) => {
                if (error.status != null) {
                    return Observable.throw({status: error.status, message: JSON.parse(error._body).message});
                }
                return Observable.throw(error.json().error || 'Server error')
            });
    }
}