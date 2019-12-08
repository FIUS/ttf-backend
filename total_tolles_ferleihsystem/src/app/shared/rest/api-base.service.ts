
import { throwError as observableThrowError,  Observable, AsyncSubject } from 'rxjs';

import { catchError } from 'rxjs/operators';
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

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

    private base: string = (window as any).basePath;

    private runningRequests: Map<string, AsyncSubject<unknown>> = new Map<string, AsyncSubject<unknown>>();

    constructor(private http: HttpClient) {}

    private extractUrl(url: string|LinkObject|ApiLinksObject|ApiObject): string {
        if (typeof url === 'string' || url instanceof String) {
            return this.prepareRelativeUrl(url as string);
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
        return this.prepareRelativeUrl(url);
    }

    private prepareRelativeUrl(url: string): string {
        if (url.startsWith('http')) {
            return url;
        }
        let url_string: string = this.base;
        if (url_string.endsWith('/')) {
            url_string = url_string.slice(0, url_string.length - 1);
        }
        if (!url.endsWith('/')) {
            if ((url.lastIndexOf('.') < 0) || (url.lastIndexOf('/') > url.lastIndexOf('.'))) {
                url = url + '/';
            }
        }
        if (url.startsWith('/')) {
            return  url_string + url;
        } else {
            return  url_string + '/' + url;
        }
    }

    private headers(token?: string, mimetypeJSON: boolean= true): {headers: HttpHeaders, [prop: string]: any} {
        const headers: {[prop: string]: string} = {};
        if (mimetypeJSON) {
            headers['Content-Type'] = 'application/json';
        }
        if (token != null) {
            headers['Authorization'] = 'Bearer ' + token;
        }

        return { headers: new HttpHeaders(headers) };
    }

    get<T>(url: string|LinkObject|ApiLinksObject|ApiObject, token?: string, params?): Observable<T> {
        url = this.extractUrl(url);
        if (this.runningRequests.has(url) && params == null) {
            return this.runningRequests.get(url).asObservable() as Observable<T>;
        }
        const options = this.headers(token);
        if (params != null) {
            options.params = params;
        }

        const request = new AsyncSubject<T>();
        this.runningRequests.set(url, request);
        this.http.get<T>(url, options).pipe(
            catchError((error: any) => {
                this.runningRequests.delete(url as string);
                if (error.status != null) {
                    return observableThrowError({status: error.status,
                        message: (error._body.startsWith != null && error._body.startsWith('{')) ?
                                JSON.parse(error._body).message : error.status + ' Server error'});
                }
                return observableThrowError(error.json().error || 'Server error');
            }),
        ).subscribe((res) => {
            request.next(res);
            request.complete();
            this.runningRequests.delete(url as string);
        }, (error: any) => {
            if (error.status != null) {
                request.error({
                    status: error.status,
                    message: (error._body.startsWith != null && error._body.startsWith('{')) ? JSON.parse(error._body).message : error.status + ' Server error'}
                );
            } else {
                request.error(error.json().error || 'Server error');
            }
            this.runningRequests.delete(url as string);
        });
        return request;
    }

    put<T>(url: string|LinkObject|ApiLinksObject|ApiObject, data, token?: string): Observable<T> {
        url = this.extractUrl(url);
        return this.http.put<T>(url, JSON.stringify(data), this.headers(token)).pipe(
            catchError((error: any) => {
                if (error.status != null) {
                    return observableThrowError({status: error.status,
                        message: (error._body.startsWith != null && error._body.startsWith('{')) ?
                                JSON.parse(error._body).message : error.status + ' Server error'});
                }
                return observableThrowError(error.json().error || 'Server error')
            }),
        );
    }

    post<T>(url: string|LinkObject|ApiLinksObject|ApiObject, data, token?: string): Observable<T> {
        url = this.extractUrl(url);
        return this.http.post<T>(url, JSON.stringify(data), this.headers(token)).pipe(
            catchError((error: any) => {
                if (error.status != null) {
                    return observableThrowError({status: error.status,
                        message: (error._body.startsWith != null && error._body.startsWith('{')) ?
                                JSON.parse(error._body).message : error.status + ' Server error'});
                }
                return observableThrowError(error.json().error || 'Server error')
            }),
        );
    }

    uploadFile<T>(url: string|LinkObject|ApiLinksObject|ApiObject, data: FormData, token?: string): Observable<T> {
        url = this.extractUrl(url);
        const options = this.headers(token, false);
        return this.http.post<T>(url, data, options).pipe(
            catchError((error: any) => {
                if (error.status != null) {
                    return observableThrowError({status: error.status,
                        message: (error._body.startsWith != null && error._body.startsWith('{')) ?
                                JSON.parse(error._body).message : error.status + ' Server error'});
                }
                return observableThrowError(error.json().error || 'Server error')
            }),
        );
    }

    downloadFile(url: string|LinkObject|ApiLinksObject|ApiObject, token?: string): Observable<Response> {
        url = this.extractUrl(url);
        const options = this.headers(token, false);
        options.responseType = 'blob';
        options.observe = 'response';
        return this.http.get<Response>(url, options).pipe(
            catchError((error: any) => {
                if (error.status != null) {
                    return observableThrowError({status: error.status,
                        message: (error._body.startsWith != null && error._body.startsWith('{')) ?
                                JSON.parse(error._body).message : error.status + ' Server error'});
                }
                return observableThrowError(error || 'Server error')
            }),
        );
    }

    delete<T>(url: string|LinkObject|ApiLinksObject|ApiObject, token?: string, data?): Observable<T> {
        url = this.extractUrl(url);
        const options = this.headers(token);
        if (data != null) {
            options.body = data;
        }
        return this.http.delete<T>(url, options).pipe(
            catchError((error: any) => {
                if (error.status != null) {
                    return observableThrowError({status: error.status,
                        message: (error._body.startsWith != null && error._body.startsWith('{')) ?
                                JSON.parse(error._body).message : error.status + ' Server error'});
                }
                return observableThrowError(error.json().error || 'Server error')
            }),
        );
    }
}
