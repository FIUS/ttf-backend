import { Injectable, OnInit } from '@angular/core';
import { Observable, } from 'rxjs/Rx';
import { BaseApiService, ApiObject, LinkObject, ApiLinksObject } from './api-base.service';
import { JWTService } from './jwt.service';
import { AsyncSubject } from 'rxjs/AsyncSubject';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';


export interface RootLinks extends ApiLinksObject {
    doc: LinkObject;
    spec: LinkObject;
    auth: LinkObject;
};

export interface RootModel extends ApiObject {
    _links: RootLinks;
    [propName: string]: any;
};


export interface AuthRootLinks extends ApiLinksObject {
    login: LinkObject;
    check: LinkObject;
    refresh_login: LinkObject;
};

export interface AuthRootModel extends ApiObject {
    _links: RootLinks;
    [propName: string]: any;
};


@Injectable()
export class ApiService implements OnInit {

    private rootSource = new AsyncSubject<RootModel>();

    private currentRoot = this.rootSource.asObservable();

    private specSource = new AsyncSubject<any>();

    private currentSpec = this.specSource.asObservable();

    private authSource = new AsyncSubject<AuthRootModel>();

    private currentAuth = this.authSource.asObservable();

    private streams: {[propName: string]: BehaviorSubject<ApiObject | ApiObject[]>} = {};

    constructor(private rest: BaseApiService, private jwt: JWTService) { }

    ngOnInit(): void {
        this.getRoot();
    }

    getRoot(): Observable<RootModel> {
        if (!this.rootSource.isStopped) {
            let url = '/api'
            if ((window as any).apiBasePath != null) {
                url = (window as any).apiBasePath;
            }
            this.rest.get(url).subscribe(data => {
                this.rootSource.next((data as RootModel));
                this.rootSource.complete();
            });
        }
        return this.currentRoot;
    }

    getSpec(): Observable<any> {
        this.getRoot().subscribe(root => {
            if (!this.specSource.isStopped) {
                const re = /\/$/;
                const url = root._links.spec.href.replace(re, '');
                this.rest.get(url).subscribe(data => {
                    this.specSource.next((data as any));
                    this.specSource.complete();
                });
            }
        });
        return this.currentSpec;
    }

    getAuthRoot(): Observable<AuthRootModel> {
        this.getRoot().subscribe(root => {
            if (!this.authSource.isStopped) {
                this.rest.get(root._links.auth).subscribe(data => {
                    this.authSource.next((data as any));
                    this.authSource.complete();
                });
            }
        });
        return this.currentAuth;
    }

    login(username: string, password: string) {
        this.getAuthRoot().subscribe(auth => {
            this.rest.post(auth._links.login, {username: username, password: password}).subscribe(data => {
                this.jwt.updateTokens(data.access_token, data.refresh_token);
                console.log(this.jwt.isAdmin());
            });
        });
    }

    ////////////////////////////////////////////////////////////////////////////

    private getStreamSource(streamID: string) {
        if (this.streams[streamID] == null) {
            this.streams[streamID] = new BehaviorSubject<ApiObject | ApiObject[]>(undefined);
        }
        return this.streams[streamID]
    }

        /*
    getPeople(): Observable<Array<ApiObject>> {
        let stream = this.getStreamSource('persons');
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.person).subscribe(data => {
                stream.next(data);
            });
        });
        return (stream.asObservable() as Observable<ApiObject[]>);
    }

    private personUpdate(data: ApiObject) {
        let stream = this.getStreamSource('persons/' + data.id);
        stream.next(data);
        // TODO update list
        this.getPeople();
    }

    getPerson(id: number): Observable<ApiObject> {
        let stream = this.getStreamSource('persons/' + id);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.person.href + id).subscribe(data => {
                this.personUpdate(data as ApiObject);
            });
        });
        return (stream.asObservable() as Observable<ApiObject>);
    }

    postPerson(newData): Observable<ApiObject> {
        return this.getRoot().flatMap(root => {
            return this.rest.post(root._links.person, newData).flatMap(data => {
                let stream = this.getStreamSource('persons/' + data.id);
                this.personUpdate(data as ApiObject);
                return (stream.asObservable() as Observable<ApiObject>);
            });
        });
    }
    */
}
