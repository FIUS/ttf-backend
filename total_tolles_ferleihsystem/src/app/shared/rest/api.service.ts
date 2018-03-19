import { Injectable, OnInit, Injector } from '@angular/core';
import { Observable, } from 'rxjs/Rx';
import { BaseApiService, ApiObject, LinkObject, ApiLinksObject } from './api-base.service';
import { JWTService } from './jwt.service';
import { InfoService } from '../info/info.service';
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
    item_tags: LinkObject;
};

export interface CatalogModel extends ApiObject {
    _links: CatalogLinks;
    [propName: string]: any;
};


@Injectable()
export class ApiService implements OnInit {

    private jwtSource = new AsyncSubject<JWTService>();
    private currentJWT = this.jwtSource.asObservable();

    private warningSet = new Set([404, 409, ]);

    private errorSet = new Set([500, 501, ]);

    private rootSource = new AsyncSubject<RootModel>();
    private currentRoot = this.rootSource.asObservable();

    private specSource = new AsyncSubject<any>();
    private currentSpec = this.specSource.asObservable();

    private catalogSource = new AsyncSubject<CatalogModel>();
    private currentCatalog = this.catalogSource.asObservable();

    private authSource = new AsyncSubject<AuthRootModel>();
    private currentAuth = this.authSource.asObservable();

    private streams: {[propName: string]: BehaviorSubject<ApiObject | ApiObject[]>} = {};

    constructor(private rest: BaseApiService, private info: InfoService, private injector: Injector) {
        Observable.timer(0).take(1).subscribe((() => {
            this.ngOnInit()
        }).bind(this))
    }

    ngOnInit(): void {
        this.jwtSource.next(this.injector.get(JWTService));
        this.jwtSource.complete();
        this.getRoot();
        this.getCatalog();
        this.getAuthRoot();
    }

    private errorHandler(error, resource: string, method: string) {
        let title;
        let message = 'Unknown Error.';
        switch (method) {
            case 'POST':
                title = 'Error while creating new resource under "' + resource + '".';
                break;
            case 'PUT':
                title = 'Error while updating existing resource "' + resource + '".';
                break;
            case 'DELETE':
                title = 'Error while deleting existing resource "' + resource + '".';
                break;

            default:
                title = 'Error while retrieving resource "' + resource + '".'
                break;
        }
        if (error.message != null) {
            message = error.message;
        }

        if (this.errorSet.has(error.status)) {
            this.info.emitError(message, title);
        } else if (this.warningSet.has(error.status)) {
            this.info.emitWarning(message, title, 7000);
        } else {
            this.info.emitInfo(message, title, 5000);
        }
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
                this.currentJWT.subscribe(jwt => jwt.updateTokens(data.access_token, data.refresh_token));
                success.next(true);
                success.complete();
            }, error => {
                if (error.status === 401 ) {
                    this.info.emitWarning('Wrong username or password!', null, 5000);
                } else {
                    this.info.emitError('Something went wrong with that login. Please try again.', 'Ooops', 10000);
                }
                success.next(false);
                success.complete();
            });
        });
        return success.asObservable();
    }

    guestLogin() {
        this.getAuthRoot().subscribe(auth => {
            this.rest.post(auth._links.guest_login, {}).subscribe(data => {
                this.currentJWT.subscribe(jwt => jwt.updateTokens(data.access_token, data.refresh_token));
            });
        });
    }

    refreshLogin(refreshToken: string) {
        this.getAuthRoot().subscribe(auth => {
            this.rest.post(auth._links.refresh, {}, refreshToken).subscribe(data => {
                this.currentJWT.subscribe(jwt => jwt.updateTokens(data.access_token));
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
                if (index < 0) {
                    list.push(data);
                } else {
                    list[index] = data;
                }
                list_stream.next(list);
            }
        }
    }

    private removeResource(streamID: string, id: number) {
        const stream = this.getStreamSource(streamID + '/' + id);
        stream.next(null);

        const list_stream = this.getStreamSource(streamID, false);
        if (list_stream != null) {
            const list: ApiObject[] = (list_stream.getValue() as ApiObject[]);
            if (list != null) {
                const index = list.findIndex(value => value.id === id);
                if (index >= 0) {
                    list.splice(index, 1);
                }
                list_stream.next(list);
            }
        }
    }


    // Item Types //////////////////////////////////////////////////////////////
    getItemTypes(): Observable<Array<ApiObject>> {
        const resource = 'item_types';
        const stream = this.getStreamSource(resource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.get(catalog._links.item_types, token).subscribe(data => {
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET'));
            }, error => this.errorHandler(error, resource, 'GET'));
        });

        return (stream.asObservable() as Observable<ApiObject[]>).filter(data => data != null);
    }

    getItemType(id: number): Observable<ApiObject> {
        const baseResource = 'item_types';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.get(catalog._links.item_types.href + id, token).subscribe(data => {
                    this.updateResource(baseResource, data as ApiObject);
                }, error => this.errorHandler(error, resource, 'GET'));
            }, error => this.errorHandler(error, resource, 'GET'));
        });

        return (stream.asObservable() as Observable<ApiObject>).filter(data => data != null);
    }

    postItemType(newData): Observable<ApiObject> {
        const resource = 'item_types';

        return this.currentJWT.map(jwt => jwt.token()).flatMap(token => {
            return this.getCatalog().flatMap(catalog => {
                return this.rest.post(catalog._links.item_types, newData, token).flatMap(data => {
                    const stream = this.getStreamSource(resource + '/' + data.id);
                    this.updateResource(resource, data);
                    return (stream.asObservable() as Observable<ApiObject>).filter(data => data != null);
                })
                .catch(error => {
                    this.errorHandler(error, resource, 'POST');
                    return Observable.throw(error);
                });
            });
        });
    }

    putItemType(id: number, newData): Observable<ApiObject> {
        const baseResource = 'item_types';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.put(catalog._links.item_types.href + id + '/', newData, token).subscribe(data => {
                    this.updateResource(baseResource, data as ApiObject);
                }, error => this.errorHandler(error, resource, 'PUT'));
            }, error => this.errorHandler(error, resource, 'PUT'));
        });

        return (stream.asObservable() as Observable<ApiObject>).filter(data => data != null);
    }

    deleteItemType(id: number): Observable<ApiObject> {
        const baseResource = 'item_types';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.delete(catalog._links.item_types.href + id + '/', token).subscribe(() => {
                    this.removeResource(baseResource, id);
                }, error => this.errorHandler(error, resource, 'DELETE'));
            }, error => this.errorHandler(error, resource, 'DELETE'));
        });

        return (stream.asObservable() as Observable<ApiObject>).filter(data => data != null);
    }



    // Tags ////////////////////////////////////////////////////////////////////
    getTags(): Observable<Array<ApiObject>> {
        const resource = 'tags';
        const stream = this.getStreamSource(resource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.get(catalog._links.item_tags, token).subscribe(data => {
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET'));
            }, error => this.errorHandler(error, resource, 'GET'));
        });

        return (stream.asObservable() as Observable<ApiObject[]>).filter(data => data != null);
    }

    getTag(id: number): Observable<ApiObject> {
        const baseResource = 'tags';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.get(catalog._links.item_tags.href + id, token).subscribe(data => {
                    this.updateResource(baseResource, data as ApiObject);
                }, error => this.errorHandler(error, resource, 'GET'));
            }, error => this.errorHandler(error, resource, 'GET'));
        });

        return (stream.asObservable() as Observable<ApiObject>).filter(data => data != null);
    }

    postTag(newData): Observable<ApiObject> {
        const resource = 'tags';

        return this.currentJWT.map(jwt => jwt.token()).flatMap(token => {
            return this.getCatalog().flatMap(catalog => {
                return this.rest.post(catalog._links.item_tags, newData, token).flatMap(data => {
                    const stream = this.getStreamSource(resource + '/' + data.id);
                    this.updateResource(resource, data);
                    return (stream.asObservable() as Observable<ApiObject>).filter(data => data != null);
                })
                .catch(error => {
                    this.errorHandler(error, resource, 'POST');
                    return Observable.throw(error);
                });
            });
        });
    }

    putTag(id: number, newData): Observable<ApiObject> {
        const baseResource = 'tags';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.put(catalog._links.item_tags.href + id + '/', newData, token).subscribe(data => {
                    this.updateResource(baseResource, data as ApiObject);
                }, error => this.errorHandler(error, resource, 'PUT'));
            }, error => this.errorHandler(error, resource, 'PUT'));
        });

        return (stream.asObservable() as Observable<ApiObject>).filter(data => data != null);
    }

    deleteTag(id: number): Observable<ApiObject> {
        const baseResource = 'tags';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.delete(catalog._links.item_tags.href + id + '/', token).subscribe(() => {
                    this.removeResource(baseResource, id);
                }, error => this.errorHandler(error, resource, 'DELETE'));
            }, error => this.errorHandler(error, resource, 'DELETE'));
        });

        return (stream.asObservable() as Observable<ApiObject>).filter(data => data != null);
    }



    // Attribute Definitions ///////////////////////////////////////////////////
    getAttributeDefinitions(): Observable<Array<ApiObject>> {
        const resource = 'attribute_definitions';
        const stream = this.getStreamSource(resource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.get(catalog._links.attribute_definitions, token).subscribe(data => {
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET'));
            }, error => this.errorHandler(error, resource, 'GET'));
        });

        return (stream.asObservable() as Observable<ApiObject[]>).filter(data => data != null);
    }

    getAttributeDefinition(id: number): Observable<ApiObject> {
        const baseResource = 'attribute_definitions';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.get(catalog._links.attribute_definitions.href + id, token).subscribe(data => {
                    this.updateResource(baseResource, data as ApiObject);
                }, error => this.errorHandler(error, resource, 'GET'));
            }, error => this.errorHandler(error, resource, 'GET'));
        });

        return (stream.asObservable() as Observable<ApiObject>).filter(data => data != null);
    }

    postAttributeDefinition(newData): Observable<ApiObject> {
        const resource = 'attribute_definitions';

        return this.currentJWT.map(jwt => jwt.token()).flatMap(token => {
            return this.getCatalog().flatMap(catalog => {
                return this.rest.post(catalog._links.attribute_definitions, newData, token).flatMap(data => {
                    const stream = this.getStreamSource(resource + '/' + data.id);
                    this.updateResource(resource, data);
                    return (stream.asObservable() as Observable<ApiObject>).filter(data => data != null);
                })
                .catch(error => {
                    this.errorHandler(error, resource, 'POST');
                    return Observable.throw(error);
                });
            });
        });
    }

    putAttributeDefinition(id: number, newData): Observable<ApiObject> {
        const baseResource = 'attribute_definitions';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.put(catalog._links.attribute_definitions.href + id + '/', newData, token).subscribe(data => {
                    this.updateResource(baseResource, data as ApiObject);
                }, error => this.errorHandler(error, resource, 'PUT'));
            }, error => this.errorHandler(error, resource, 'PUT'));
        });

        return (stream.asObservable() as Observable<ApiObject>).filter(data => data != null);
    }

    deleteAttributeDefinition(id: number): Observable<ApiObject> {
        const baseResource = 'attribute_definitions';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.delete(catalog._links.attribute_definitions.href + id + '/', token).subscribe(() => {
                    this.removeResource(baseResource, id);
                }, error => this.errorHandler(error, resource, 'DELETE'));
            }, error => this.errorHandler(error, resource, 'DELETE'));
        });

        return (stream.asObservable() as Observable<ApiObject>).filter(data => data != null);
    }

    getLinkedAttributeDefinitions(linkedObject: ApiObject): Observable<ApiObject[]> {
        const url = linkedObject._links.attributes.href;
        const resource = new URL(url).pathname.replace(/(^.*catalog\/)|(\/$)/, '');
        const stream = this.getStreamSource(resource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.rest.get(url, token).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        });

        return (stream.asObservable() as Observable<ApiObject[]>).filter(data => data != null);
    }

    linkAttributeDefinition(linkedObject: ApiObject, attributeDefinition: ApiObject): Observable<ApiObject[]> {
        const url = linkedObject._links.attributes.href;
        const resource = new URL(url).pathname.replace(/(^.*catalog\/)|(\/$)/, '');
        const stream = this.getStreamSource(resource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.rest.post(url, attributeDefinition, token).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'POST'));
        });

        return (stream.asObservable() as Observable<ApiObject[]>).filter(data => data != null);
    }

    unlinkAttributeDefinition(linkedObject: ApiObject, attributeDefinition: ApiObject): Observable<ApiObject[]> {
        const url = linkedObject._links.attributes.href;
        const baseResource = new URL(url).pathname.replace(/(^.*catalog\/)|(\/$)/, '');
        const resource = baseResource + attributeDefinition.id;
        const stream = this.getStreamSource(baseResource);

        this.currentJWT.map(jwt => jwt.token()).subscribe(token => {
            this.rest.delete(url + attributeDefinition.id, token).subscribe(data => {
                this.getLinkedAttributeDefinitions(linkedObject);
            }, error => this.errorHandler(error, resource, 'DELETE'));
        });

        return (stream.asObservable() as Observable<ApiObject[]>).filter(data => data != null);
    }
}
