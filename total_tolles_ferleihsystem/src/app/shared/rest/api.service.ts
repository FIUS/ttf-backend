import { Injectable, OnInit, Injector } from '@angular/core';
import { Observable, } from 'rxjs/Rx';
import { BaseApiService, ApiObject, LinkObject, ApiLinksObject } from './api-base.service';
import { JWTService } from './jwt.service';
import { AsyncSubject } from 'rxjs/AsyncSubject';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';


export interface RootLinks extends ApiLinksObject {
    doc: LinkObject;
    spec: LinkObject;
    auth: LinkObject;
    catalog: LinkObject;
};

export interface RootModel extends ApiObject {
    _links: RootLinks;
    [propName: string]: any;
};


export interface AuthRootLinks extends ApiLinksObject {
    login: LinkObject;
    guest_login: LinkObject;
    fresh_login: LinkObject;
    refresh: LinkObject;
    check: LinkObject;
};

export interface AuthRootModel extends ApiObject {
    _links: AuthRootLinks;
    [propName: string]: any;
};


export interface CatalogLinks extends ApiLinksObject {
    item_types: LinkObject;
};

export interface CatalogModel extends ApiObject {
    _links: CatalogLinks;
    [propName: string]: any;
};


@Injectable()
export class ApiService implements OnInit {

    private jwt: JWTService;

    private rootSource = new AsyncSubject<RootModel>();

    private currentRoot = this.rootSource.asObservable();

    private specSource = new AsyncSubject<any>();

    private currentSpec = this.specSource.asObservable();

    private catalogSource = new AsyncSubject<CatalogModel>();

    private currentCatalog = this.catalogSource.asObservable();

    private authSource = new AsyncSubject<AuthRootModel>();

    private currentAuth = this.authSource.asObservable();

    private streams: {[propName: string]: BehaviorSubject<ApiObject | ApiObject[]>} = {};

    constructor(private rest: BaseApiService, private injector: Injector) {
        Observable.timer(1).take(1).subscribe((() => {
            this.ngOnInit()
        }).bind(this))
    }

    ngOnInit(): void {
        this.jwt = this.injector.get(JWTService);
        this.getRoot();
        this.getCatalog();
        this.getAuthRoot();
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

    getCatalog(): Observable<CatalogModel> {
        this.getRoot().subscribe(root => {
            if (!this.catalogSource.isStopped) {
                this.rest.get(root._links.catalog).subscribe(data => {
                    this.catalogSource.next((data as CatalogModel));
                    this.catalogSource.complete();
                });
            }
        });
        return this.currentCatalog;
    }

    getAuthRoot(): Observable<AuthRootModel> {
        this.getRoot().subscribe(root => {
            if (!this.authSource.isStopped) {
                this.rest.get(root._links.auth).subscribe(data => {
                    this.authSource.next((data as AuthRootModel));
                    this.authSource.complete();
                });
            }
        });
        return this.currentAuth;
    }

    login(username: string, password: string): Observable<boolean> {
        const success = new AsyncSubject<boolean>();
        this.getAuthRoot().subscribe(auth => {
            this.rest.post(auth._links.login, {username: username, password: password}).subscribe(data => {
                this.jwt.updateTokens(data.access_token, data.refresh_token);
                success.next(true);
                success.complete();
            }, error => {
                success.next(false);
                success.complete();
            });
        });
        return success.asObservable();
    }

    guestLogin() {
        this.getAuthRoot().subscribe(auth => {
            this.rest.post(auth._links.guest_login, {}).subscribe(data => {
                this.jwt.updateTokens(data.access_token, data.refresh_token);
            });
        });
    }

    refreshLogin(refreshToken: string) {
        this.getAuthRoot().subscribe(auth => {
            this.rest.post(auth._links.refresh, {}, refreshToken).subscribe(data => {
                this.jwt.updateTokens(data.access_token);
            });
        });
    }

    ////////////////////////////////////////////////////////////////////////////

    private getStreamSource(streamID: string, create: boolean = true) {
        if (this.streams[streamID] == null && create) {
            this.streams[streamID] = new BehaviorSubject<ApiObject | ApiObject[]>(undefined);
        }
        return this.streams[streamID];
    }

    private updateResource(streamID: string, data: ApiObject) {
        const stream = this.getStreamSource(streamID + '/' +  data.id);
        stream.next(data);
        const list_stream = this.getStreamSource(streamID, false);
        if (list_stream != null) {
            const list: ApiObject[] = (list_stream.getValue() as ApiObject[]);
            if (list != null) {
                const index = list.findIndex(value => value.id === data.id);
                list[index] = data;
                list_stream.next(list);
            }
        }
    }

    get itemTypes(): Observable<Array<ApiObject>> {
        const stream = this.getStreamSource('item_types');
        this.getCatalog().subscribe((catalog) => {
            this.rest.get(catalog._links.item_types).subscribe(data => {
                stream.next(data);
            });
        });
        return (stream.asObservable() as Observable<ApiObject[]>);
    }

    private getItemType(id: number): Observable<ApiObject> {
        const stream = this.getStreamSource('item_types/' + id);
        this.getCatalog().subscribe((catalog) => {
            this.rest.get(catalog._links.item_types.href + id).subscribe(data => {
                this.updateResource('item_types', data as ApiObject);
            });
        });
        return (stream.asObservable() as Observable<ApiObject>);
    }

    postItemType(newData): Observable<ApiObject> {
        return this.getCatalog().flatMap(catalog => {
            return this.rest.post(catalog._links.item_types, newData).flatMap(data => {
                const stream = this.getStreamSource('item_types/' + data.id);
                this.updateResource('item_types', data);
                return (stream.asObservable() as Observable<ApiObject>);
            });
        });
    }
}
