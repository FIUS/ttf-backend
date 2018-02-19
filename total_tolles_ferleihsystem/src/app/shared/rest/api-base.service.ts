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

    get(url: string|LinkObject|ApiLinksObject|ApiObject): Observable<ApiObject | ApiObject[]> {
        url = this.extractUrl(url);
        if (this.runningRequests.has(url)) {
            return this.runningRequests.get(url);
        }
        console.log(url);
        const request = this.http.get(url)
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

    private headers(): RequestOptions {
        let headers = new Headers();
        headers.append('Content-Type', 'application/json');
        // TODO headers.append('authentication', `${student.token}`);

        return new RequestOptions({ headers: headers });
    }

    put(url: string|LinkObject|ApiLinksObject|ApiObject, data): Observable<ApiObject> {
        url = this.extractUrl(url);
        return this.http.put(url, JSON.stringify(data), this.headers())
            .map((res: Response) => res.json())
            .catch((error: any) => Observable.throw(error.json().error || 'Server error'));
    }

    post(url: string|LinkObject|ApiLinksObject|ApiObject, data): Observable<ApiObject> {
        url = this.extractUrl(url);
        return this.http.post(url, JSON.stringify(data), this.headers())
            .map((res: Response) => res.json())
            .catch((error: any) => Observable.throw(error.json().error || 'Server error'));
    }
}