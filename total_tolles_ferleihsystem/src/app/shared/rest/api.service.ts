
import {throwError as observableThrowError, timer as observableTimer,  Observable, Subject, AsyncSubject ,  BehaviorSubject } from 'rxjs';

import {catchError, take, filter, mergeMap} from 'rxjs/operators';
import { Injectable, OnInit, Injector } from '@angular/core';
import { BaseApiService, ApiObject, LinkObject, ApiLinksObject } from './api-base.service';
import { JWTService } from './jwt.service';
import { InfoService } from '../info/info.service';
import { saveAs } from 'file-saver';


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

    private streams: {[propName: string]: BehaviorSubject<unknown>} = {};

    constructor(private rest: BaseApiService, private info: InfoService, private injector: Injector) {
        observableTimer(0).pipe(take(1)).subscribe((() => {
            this.ngOnInit()
        }).bind(this))
    }

    ngOnInit(): void {
        this.jwtSource.next(this.injector.get(JWTService));
        this.jwtSource.complete();
        this.getRoot();
        this.getCatalog();
        this.getItemTypes();
        this.getAuthRoot();
    }

    private errorHandler(error, resource: string, method: string, showErrors: string= 'all') {
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

        if (this.errorSet.has(error.status) && showErrors !== 'none') {
            this.info.emitError(message, title);
        } else if (this.warningSet.has(error.status) && (showErrors === 'warnings' || showErrors === 'all')) {
            this.info.emitWarning(message, title);
        } else if (showErrors === 'all') {
            this.info.emitInfo(message, title);
        }
    }

    getRoot(): Observable<RootModel> {
        if (!this.rootSource.isStopped) {
            let url = '/api'
            if ((window as any).apiBasePath != null) {
                url = (window as any).apiBasePath;
            }
            this.rest.get<RootModel>(url).subscribe(data => {
                this.rootSource.next(data);
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
                this.rest.get<any>(url).subscribe(data => {
                    this.specSource.next(data);
                    this.specSource.complete();
                });
            }
        });
        return this.currentSpec;
    }

    getCatalog(): Observable<CatalogModel> {
        this.getRoot().subscribe(root => {
            if (!this.catalogSource.isStopped) {
                this.rest.get<CatalogModel>(root._links.catalog).subscribe(data => {
                    this.catalogSource.next(data);
                    this.catalogSource.complete();
                });
            }
        });
        return this.currentCatalog;
    }

    getAuthRoot(): Observable<AuthRootModel> {
        this.getRoot().subscribe(root => {
            if (!this.authSource.isStopped) {
                this.rest.get<AuthRootModel>(root._links.auth).subscribe(data => {
                    this.authSource.next(data);
                    this.authSource.complete();
                });
            }
        });
        return this.currentAuth;
    }

    login(username: string, password: string): Observable<boolean> {
        const success = new AsyncSubject<boolean>();
        this.getAuthRoot().subscribe(auth => {
            this.rest.post<ApiObject>(auth._links.login, {username: username, password: password}).subscribe(data => {
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
            this.rest.post<ApiObject>(auth._links.guest_login, {}).subscribe(data => {
                this.currentJWT.subscribe(jwt => jwt.updateTokens(data.access_token, data.refresh_token));
            });
        });
    }

    refreshLogin(refreshToken: string) {
        this.getAuthRoot().subscribe(auth => {
            this.rest.post<ApiObject>(auth._links.refresh, {}, refreshToken).subscribe(data => {
                this.currentJWT.subscribe(jwt => jwt.updateTokens(data.access_token));
            });
        });
    }

    freshLogin = (password: string) => {
        this.currentJWT.subscribe(jwt => {
            this.getAuthRoot().subscribe(auth => {
                this.rest.post<ApiObject>(auth._links.fresh_login, { username: jwt.username(), password: password }).subscribe(data => {
                    jwt.updateTokens(data.access_token, data.refresh_token);
                });
            });
        });
    }

    getSettings(): Observable<string> {
        const stream = new AsyncSubject<string>();
        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getAuthRoot().subscribe(auth => {
                this.rest.get<ApiObject>(auth._links.settings, token).subscribe(data => {
                    stream.next(data.settings);
                    stream.complete();
                });
            });
        });
        return stream.asObservable();
    }

    updateSettings(settings: string): Observable<string> {
        const stream = new AsyncSubject<string>();
        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getAuthRoot().subscribe(auth => {
                this.rest.put<ApiObject>(auth._links.settings, {'settings': settings}, token).subscribe(data => {
                    stream.next(data.settings);
                    stream.complete();
                });
            });
        });
        return stream.asObservable();
    }

    search(search: string, type?: number, tags?: Set<number>,
           attributes?: Map<number, string>, deleted?: boolean,
           lent?: boolean, lendableOnly?: boolean): Observable<ApiObject[]> {
        const stream = new AsyncSubject<ApiObject[]>();

        const params: any = {search: search};

        if (type != null && type >= 0) {
            params.type = type;
        }

        if (tags != null && tags.size > 0) {
            params.tag = [];
            tags.forEach(tag => params.tag.push(tag));
        }

        if (attributes != null) {
            params.attrib = [];
            attributes.forEach((value, id) => {
                params.attrib.push(id.toString() + '-' + value);
            });
        }

        if (deleted != null) {
            params.deleted = deleted;
        }

        if (lent != null) {
            params.lent = lent;
        }

        if (lendableOnly != null) {
            params.lendable = lendableOnly;
        }

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getRoot().subscribe((root) => {
                this.rest.get<ApiObject[]>(root._links.search, token, params).subscribe(data => {
                    stream.next(data);
                    stream.complete();
                }, error => this.errorHandler(error, 'search', 'GET'));
            }, error => this.errorHandler(error, 'search', 'GET'));
        });

        return stream.asObservable();
    }

    ////////////////////////////////////////////////////////////////////////////

    private getStreamSource<T>(streamID: string, create: boolean = true) {
        if (this.streams[streamID] == null && create) {
            this.streams[streamID] = new BehaviorSubject<T>(undefined);
        }
        return this.streams[streamID] as BehaviorSubject<T>;
    }

    private updateResource(streamID: string, data: ApiObject, idField: string = 'id') {
        const stream = this.getStreamSource<ApiObject>(streamID + '/' +  data[idField]);
        stream.next(data);

        const list_stream = this.getStreamSource<ApiObject[]>(streamID, false);
        if (list_stream != null) {
            const list: ApiObject[] = (list_stream.getValue());
            if (list != null) {
                const newlist = [];
                let updated = false;
                list.forEach((value) => {
                    if (value[idField] === data[idField]) {
                        updated = true;
                        newlist.push(data);
                    } else {
                        newlist.push(value);
                    }
                });
                if (!updated) {
                    newlist.push(data);
                }
                list_stream.next(newlist);
            }
        }
    }

    private removeResource(streamID: string, id: number) {
        const stream = this.getStreamSource<ApiObject>(streamID + '/' + id);
        stream.next(null);

        const list_stream = this.getStreamSource<ApiObject[]>(streamID, false);
        if (list_stream != null) {
            const list: ApiObject[] = (list_stream.getValue());
            if (list != null) {
                const newlist = [];
                let updated = false;
                list.forEach((value) => {
                    if (value.id === id) {
                        updated = true;
                    } else {
                        newlist.push(value);
                    }
                });
                if (updated) {
                    list_stream.next(newlist);
                }
            }
        }
    }


    // Item Types //////////////////////////////////////////////////////////////
    getItemTypes(deleted: boolean=false, showErrors: string= 'all'): Observable<ApiObject[]> {
        let resource = 'item_types';
        let params = null;
        if (deleted) {
            resource += '?deleted=true';
            params = {deleted: true};
        }
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.get<ApiObject[]>(catalog._links.item_types, token, params).subscribe(data => {
                    stream.next(data);

                    // insert item types into detail cache streams
                    data.forEach(itemType => {
                        const detailStream = this.getStreamSource<ApiObject>(resource + '/' +  itemType.id);
                        detailStream.next(itemType);
                    });
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            }, error => this.errorHandler(error, resource, 'GET', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    getItemType(id: number, showErrors: string= 'all', preferCache: boolean= false): Observable<ApiObject> {
        const baseResource = 'item_types';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        if (!(preferCache && stream.value != null)) {
            this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
                this.getCatalog().subscribe((catalog) => {
                    this.rest.get<ApiObject>(catalog._links.item_types.href + id, token).subscribe(data => {
                        this.updateResource(baseResource, data);
                    }, error => this.errorHandler(error, resource, 'GET', showErrors));
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            });
        }

        return stream.asObservable().pipe(filter(data => data != null));
    }

    postItemType(newData, showErrors: string= 'all'): Observable<ApiObject> {
        const resource = 'item_types';

        return this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken()),mergeMap(token => {
            return this.getCatalog().pipe(
                mergeMap(catalog => {
                    return this.rest.post<ApiObject>(catalog._links.item_types, newData, token).pipe(
                        mergeMap(data => {
                            const stream = this.getStreamSource<ApiObject>(resource + '/' + data.id);
                            this.updateResource(resource, data);
                            return stream.asObservable().pipe(filter(d => d != null));
                        }),
                        catchError(error => {
                            this.errorHandler(error, resource, 'POST', showErrors);
                            return observableThrowError(error);
                        }),
                    );
                }));
            }),
        );
    }

    putItemType(id: number, newData, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'item_types';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.put<ApiObject>(catalog._links.item_types.href + id + '/', newData, token).subscribe(data => {
                    this.updateResource(baseResource, data);
                }, error => this.errorHandler(error, resource, 'PUT', showErrors));
            }, error => this.errorHandler(error, resource, 'PUT', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    deleteItemType(id: number, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'item_types';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.delete<ApiObject>(catalog._links.item_types.href + id + '/', token).subscribe(() => {
                    this.removeResource(baseResource, id);
                    this.getItemTypes(true);
                }, error => this.errorHandler(error, resource, 'DELETE', showErrors));
            }, error => this.errorHandler(error, resource, 'DELETE', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    undeleteItemType(id: number, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'item_types';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.post<ApiObject>(catalog._links.item_types.href + id + '/', undefined, token).subscribe(() => {
                    this.getItemType(id);
                    this.getItemTypes(true);
                }, error => this.errorHandler(error, resource, 'POST', showErrors));
            }, error => this.errorHandler(error, resource, 'POST', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    getContainedTypes(item_type: ApiObject, showErrors: string= 'all'): Observable<ApiObject[]> {
        const resource = 'item-types/' + item_type.id + '/contained-types';
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.get<ApiObject[]>(item_type._links.contained_types, token).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET', showErrors));
        });

        return (stream.asObservable() as Observable<ApiObject[]>);
    }

    postContainedType(item_type: ApiObject, itemTypeID, showErrors: string= 'all'): Observable<ApiObject[]> {
        const resource = 'item-types/' + item_type.id + '/contained-types';
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.post<ApiObject[]>(item_type._links.contained_types, {id: itemTypeID}, token).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'POST', showErrors));
        });

        return (stream.asObservable() as Observable<ApiObject[]>);
    }

    deleteContainedType(item_type: ApiObject, itemTypeID, showErrors: string= 'all'): Observable<ApiObject[]> {
        const resource = 'item-types/' + item_type.id + '/contained-types';
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.delete<ApiObject[]>(item_type._links.contained_types, token, {id: itemTypeID}).subscribe(data => {
                this.getContainedTypes(item_type);
            }, error => this.errorHandler(error, resource, 'DELETE', showErrors));
        });

        return (stream.asObservable() as Observable<ApiObject[]>);
    }



    // Tags ////////////////////////////////////////////////////////////////////
    getTags(deleted: boolean= false, showErrors: string= 'all'): Observable<ApiObject[]> {
        let resource = 'tags';
        let params = null;
        if (deleted) {
            resource += '?deleted=true';
            params = {deleted: true};
        }
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.get<ApiObject[]>(catalog._links.item_tags, token, params).subscribe(data => {
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            }, error => this.errorHandler(error, resource, 'GET', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    getTag(id: number, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'tags';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(
            mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
                this.getCatalog().subscribe((catalog) => {
                    this.rest.get<ApiObject>(catalog._links.item_tags.href + id, token).subscribe(data => {
                        this.updateResource(baseResource, data);
                    }, error => this.errorHandler(error, resource, 'GET', showErrors));
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            }
        );

        return stream.asObservable().pipe(filter(data => data != null));
    }

    postTag(newData, showErrors: string= 'all'): Observable<ApiObject> {
        const resource = 'tags';

        return this.currentJWT.pipe(
            mergeMap(jwt => jwt.getValidApiToken()),
            mergeMap(token => {
                return this.getCatalog().pipe(
                    mergeMap(catalog => {
                        return this.rest.post<ApiObject>(catalog._links.item_tags, newData, token).pipe(mergeMap(data => {
                            const stream = this.getStreamSource<ApiObject>(resource + '/' + data.id);
                            this.updateResource(resource, data);
                            return (stream.asObservable() as Observable<ApiObject>).pipe(filter(d => d != null));
                        }),
                        catchError(error => {
                            this.errorHandler(error, resource, 'POST', showErrors);
                            return observableThrowError(error);
                        }),
                    );
                }));
            }),
        );
    }

    putTag(id: number, newData, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'tags';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.put<ApiObject>(catalog._links.item_tags.href + id + '/', newData, token).subscribe(data => {
                    this.updateResource(baseResource, data);
                }, error => this.errorHandler(error, resource, 'PUT', showErrors));
            }, error => this.errorHandler(error, resource, 'PUT', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    deleteTag(id: number, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'tags';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.delete<ApiObject>(catalog._links.item_tags.href + id + '/', token).subscribe(() => {
                    this.removeResource(baseResource, id);
                }, error => this.errorHandler(error, resource, 'DELETE', showErrors));
            }, error => this.errorHandler(error, resource, 'DELETE', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    undeleteTag(id: number, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'tags';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.post<ApiObject>(catalog._links.item_tags.href + id + '/', undefined, token).subscribe(() => {
                    this.getTag(id);
                    this.getTags(true);
                }, error => this.errorHandler(error, resource, 'POST', showErrors));
            }, error => this.errorHandler(error, resource, 'POST', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }



    // Attribute Definitions ///////////////////////////////////////////////////
    getAttributeDefinitions(deleted: boolean=false, showErrors: string= 'all'): Observable<ApiObject[]> {
        let resource = 'attribute_definitions';
        let params = null;
        if (deleted) {
            resource += '?deleted=true';
            params = {deleted: true};
        }
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.get<ApiObject[]>(catalog._links.attribute_definitions, token, params).subscribe(data => {
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            }, error => this.errorHandler(error, resource, 'GET', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    getAttributeDefinition(id: number, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'attribute_definitions';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.get<ApiObject>(catalog._links.attribute_definitions.href + id, token).subscribe(data => {
                    this.updateResource(baseResource, data);
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            }, error => this.errorHandler(error, resource, 'GET', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    postAttributeDefinition(newData, showErrors: string= 'all'): Observable<ApiObject> {
        const resource = 'attribute_definitions';

        return this.currentJWT.pipe(
            mergeMap(jwt => jwt.getValidApiToken()),
            mergeMap(token => {
                return this.getCatalog().pipe(
                    mergeMap(catalog => {
                        return this.rest.post<ApiObject>(catalog._links.attribute_definitions, newData, token).pipe(mergeMap(data => {
                            const stream = this.getStreamSource<ApiObject>(resource + '/' + data.id);
                            this.updateResource(resource, data);
                            return (stream.asObservable() as Observable<ApiObject>).pipe(filter(d => d != null));
                        }),
                        catchError(error => {
                            this.errorHandler(error, resource, 'POST', showErrors);
                            return observableThrowError(error);
                        }),
                    );
                }));
            }),
        );
    }

    putAttributeDefinition(id: number, newData, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'attribute_definitions';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.put<ApiObject>(catalog._links.attribute_definitions.href + id + '/', newData, token).subscribe(data => {
                    this.updateResource(baseResource, data);
                }, error => this.errorHandler(error, resource, 'PUT', showErrors));
            }, error => this.errorHandler(error, resource, 'PUT', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    deleteAttributeDefinition(id: number, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'attribute_definitions';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.delete<ApiObject>(catalog._links.attribute_definitions.href + id + '/', token).subscribe(() => {
                    this.removeResource(baseResource, id);
                }, error => this.errorHandler(error, resource, 'DELETE', showErrors));
            }, error => this.errorHandler(error, resource, 'DELETE', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    undeleteAttributeDefinition(id: number, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'attribute_definitions';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.post<ApiObject>(catalog._links.attribute_definitions.href + id + '/', undefined, token).subscribe(() => {
                    this.getAttributeDefinition(id);
                    this.getAttributeDefinitions(true);
                }, error => this.errorHandler(error, resource, 'POST', showErrors));
            }, error => this.errorHandler(error, resource, 'POST', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    getAttributeAutocomplete(attrDef: ApiObject, showErrors: string= 'all'): Observable<any[]> {
        const resource = 'attribute_definitions/' + attrDef.id + '/autocomplete';
        const stream: BehaviorSubject<any[]> = this.getStreamSource<any[]>(resource);
        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.get<string[]>(attrDef._links.autocomplete, token).subscribe(data => {
                const parsed = [];
                if (data != null && data.length > 0) {
                    data.forEach(element => {
                        try {
                            parsed.push(JSON.parse(element));
                        } catch (error) {}
                    });
                }
                stream.next(parsed);
            });
        });
        return stream.asObservable();
    }

    getLinkedAttributeDefinitions(linkedObject: ApiObject, showErrors: string= 'all'): Observable<ApiObject[]> {
        let url: string = linkedObject._links.attributes.href;
        if (url.startsWith('http')) {
            url = new URL(url).pathname;
        }
        const resource = url.replace(/(^.*catalog\/)|(\/$)/, '');
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.get<ApiObject[]>(url, token).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    linkAttributeDefinition(linkedObject: ApiObject, attributeDefinition: ApiObject, showErrors: string= 'all'): Observable<ApiObject[]> {
        let url: string = linkedObject._links.attributes.href;
        if (url.startsWith('http')) {
            url = new URL(url).pathname;
        }
        const resource = url.replace(/(^.*catalog\/)|(\/$)/, '');
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.post<ApiObject[]>(url, attributeDefinition, token).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'POST', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    unlinkAttributeDefinition(linkedObject: ApiObject, attributeDefinition: ApiObject, showErrors: string= 'all'): Observable<ApiObject[]> {
        let url: string = linkedObject._links.attributes.href;
        if (url.startsWith('http')) {
            url = new URL(url).pathname;
        }
        const baseResource = url.replace(/(^.*catalog\/)|(\/$)/, '');
        const resource = baseResource + attributeDefinition.id;
        const stream = this.getStreamSource<ApiObject[]>(baseResource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.delete<ApiObject[]>(url, token, attributeDefinition).subscribe(data => {
                this.getLinkedAttributeDefinitions(linkedObject);
            }, error => this.errorHandler(error, resource, 'DELETE', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }



    // Items ///////////////////////////////////////////////////////////////////
    getItems(deleted: boolean= false, showErrors: string= 'all'): Observable<ApiObject[]> {
        let resource = 'items';
        let params = null;
        if (deleted) {
            resource += '?deleted=true';
            params = {deleted: true};
        }
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.get<ApiObject[]>(catalog._links.items, token, params).subscribe(data => {
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            }, error => this.errorHandler(error, resource, 'GET', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    getLentItems(showErrors: string= 'all'): Observable<ApiObject[]> {
        const resource = 'items?lent=true';
        const params =  {lent: true};
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.get<ApiObject[]>(catalog._links.items, token, params).subscribe(data => {
                    data.sort((a, b) => {
                        if (a.due == null || a.due == '') {
                            return -1;
                        }
                        if (b.due == null || b.due == '') {
                            return 1;
                        }
                        const d_a = new Date(a.due * 1000);
                        const d_b = new Date(b.due * 1000);
                        if (d_a < d_b) {
                            return -1;
                        } else if (d_a > d_b) {
                            return 1;
                        } else {
                            return 0;
                        }
                    });
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            }, error => this.errorHandler(error, resource, 'GET', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    getItem(id: number, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'items';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.get<ApiObject>(catalog._links.items.href + id, token).subscribe(data => {
                    this.updateResource(baseResource, data);
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            }, error => this.errorHandler(error, resource, 'GET', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    postItem(newData, showErrors: string= 'all'): Observable<ApiObject> {
        const resource = 'items';

        return this.currentJWT.pipe(
            mergeMap(jwt => jwt.getValidApiToken()),
                mergeMap(token => {
                return this.getCatalog().pipe(mergeMap(catalog => {
                    return this.rest.post<ApiObject>(catalog._links.items, newData, token).pipe(
                        mergeMap(data => {
                            const stream = this.getStreamSource<ApiObject>(resource + '/' + data.id);
                            this.updateResource(resource, data);
                            return (stream.asObservable() as Observable<ApiObject>).pipe(filter(d => d != null));
                        }),
                        catchError(error => {
                            this.errorHandler(error, resource, 'POST', showErrors);
                            return observableThrowError(error);
                        }),
                    );
                }));
            }),
        );
    }

    putItem(id: number, newData, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'items';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                // reset dependent caches!
                this.getStreamSource<ApiObject[]>(resource + '/attributes').next([]);
                this.rest.put<ApiObject>(catalog._links.items.href + id + '/', newData, token).subscribe(data => {
                    this.updateResource(baseResource, data);
                }, error => this.errorHandler(error, resource, 'PUT', showErrors));
            }, error => this.errorHandler(error, resource, 'PUT', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    deleteItem(id: number, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'items';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.delete<ApiObject>(catalog._links.items.href + id + '/', token).subscribe(() => {
                    this.removeResource(baseResource, id);
                    this.getItems(true);
                }, error => this.errorHandler(error, resource, 'DELETE', showErrors));
            }, error => this.errorHandler(error, resource, 'DELETE', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    undeleteItem(id: number, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'items';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe((catalog) => {
                this.rest.post<ApiObject>(catalog._links.items.href + id + '/', undefined, token).subscribe(() => {
                    this.getItem(id);
                    this.getItems(true);
                }, error => this.errorHandler(error, resource, 'POST', showErrors));
            }, error => this.errorHandler(error, resource, 'POST', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    getTagsForItem(item: ApiObject, showErrors: string= 'all', preferCache: boolean= false): Observable<ApiObject[]> {
        const resource = 'items/' + item.id + '/tags';
        const stream = this.getStreamSource<ApiObject[]>(resource);

        if (!(preferCache && stream.value != null)) {
            this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
                this.rest.get<ApiObject[]>(item._links.tags.href, token).subscribe(data => {
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            });
        }

        return stream.asObservable().pipe(filter(data => data != null));
    }

    addTagToItem(item: ApiObject, tag: ApiObject, showErrors: string= 'all'): Observable<ApiObject[]> {
        const resource = 'items/' + item.id + '/tags';
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.post<ApiObject[]>(item._links.tags.href, tag, token).subscribe(data => {
                stream.next(data);
                this.getAttributes(item);
            }, error => this.errorHandler(error, resource, 'POST', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    removeTagFromItem(item: ApiObject, tag: ApiObject, showErrors: string= 'all'): Observable<ApiObject[]> {
        const resource = 'items/' + item.id + '/tags';
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.delete<ApiObject[]>(item._links.tags.href, token, tag).subscribe(data => {
                stream.next(data);
                this.getTagsForItem(item);
                this.getAttributes(item);
            }, error => this.errorHandler(error, resource, 'DELETE', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    getContainedItems(item: ApiObject, showErrors: string= 'all'): Observable<ApiObject[]> {
        const resource = 'items/' + item.id + '/contained-items';
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.get<ApiObject[]>(item._links.contained_items, token).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    postContainedItem(item: ApiObject, itemID, showErrors: string= 'all'): Observable<ApiObject[]> {
        const resource = 'items/' + item.id + '/contained-items';
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.post<ApiObject[]>(item._links.contained_items.href, {id: itemID}, token).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'POST', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    deleteContainedItem(item: ApiObject, itemID, showErrors: string= 'all'): Observable<ApiObject[]> {
        const resource = 'items/' + item.id + '/contained-items';
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.delete<ApiObject[]>(item._links.contained_items.href, token, {id: itemID}).subscribe(data => {
                this.getContainedItems(item);
            }, error => this.errorHandler(error, resource, 'DELETE', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }



    // Files ///////////////////////////////////////////////////////////////////
    getFiles(item: ApiObject, showErrors: string= 'all'): Observable<ApiObject[]> {
        let url;
        let resource = 'files';

        if (item != null) {
            resource = 'items/' + item.id + '/files';
            url = item._links.files;
        }

        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            if (item != null) {
                this.rest.get<ApiObject[]>(url, token).subscribe(data => {
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            } else {
                this.getCatalog().subscribe(catalog => {
                    url = catalog._links.files;
                    this.rest.get<ApiObject[]>(url, token).subscribe(data => {
                        stream.next(data);
                    }, error => this.errorHandler(error, resource, 'GET', showErrors));
                })
            }
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    getFile(fileID: number, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'files';
        const resource = baseResource + '/' + fileID;

        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe(catalog => {
                this.rest.get<ApiObject>(catalog._links.files.href + fileID, token).subscribe(data => {
                    this.updateResource(baseResource, data);
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            })
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    uploadFile(item: ApiObject, file: File, showErrors: string= 'all'): Observable<ApiObject> {
        const resource = 'files';
        const stream = new AsyncSubject<ApiObject>();

        const formData = new FormData();
        formData.append('item_id', item.id);
        formData.append('file', file);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe(catalog => {
                this.rest.uploadFile<ApiObject>(catalog._links.files, formData, token).subscribe(data => {
                    stream.next(data);
                    stream.complete();
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            });
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    downloadFile(file: ApiObject, showErrors: string= 'all') {
        const stream = new AsyncSubject<any>();

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.downloadFile(file._links.download, token).subscribe(data => {
                stream.next(data);
                stream.complete();
            }, error => this.errorHandler(error, 'file-store/' + 'file.file_hash', 'GET', showErrors));
        });

        stream.subscribe(data => {
            const dispositonHeader = data.headers.get('content-disposition')
            const blob = new Blob([data.body], {type: 'application/pdf'}); //octet-stream
            saveAs(blob, dispositonHeader.length > 25 ? dispositonHeader.substring(21) : file.name + file.file_type);
        })
    }

    putFile(id: number, data, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'files';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getCatalog().subscribe(catalog => {
                this.rest.put<ApiObject>(catalog._links.files.href + id + '/', data, token).subscribe(data => {
                    this.updateResource(baseResource, data);
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            });
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    deleteFile(file: ApiObject, item?: ApiObject,  showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'files';
        const resource = baseResource + '/' + file.id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.delete<ApiObject>(file, token).subscribe(data => {
                stream.next(null);
                this.getFiles(item, showErrors);
            }, error => this.errorHandler(error, resource, 'DELETE', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }



    // Attributes //////////////////////////////////////////////////////////////
    getAttributes(item: ApiObject, showErrors: string= 'all', preferCache: boolean= false): Observable<ApiObject[]> {
        const resource = 'items/' + item.id + '/attributes';
        const stream = this.getStreamSource<ApiObject[]>(resource);

        if (!(preferCache && stream.value != null)) {
            this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
                this.rest.get<ApiObject[]>(item._links.attributes, token).subscribe(data => {
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            });
        }

        return stream.asObservable().pipe(filter(data => data != null));
    }

    getAttribute(item: ApiObject, id: number, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'items/' + item.id + '/attributes';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.get<ApiObject>(item._links.attributes.href + id + '/', token).subscribe(data => {
                this.updateResource(baseResource, data, 'attribute_definition_id');
            }, error => this.errorHandler(error, resource, 'GET', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    putAttribute(item: ApiObject, id: number, value, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'items/' + item.id + '/attributes';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.put<ApiObject>(item._links.attributes.href + id + '/', {value: value}, token).subscribe(data => {
                this.updateResource(baseResource, data, 'attribute_definition_id');
                this.getItem(item.id);
            }, error => this.errorHandler(error, resource, 'GET', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }



    // Lendings ////////////////////////////////////////////////////////////////
    getLendings(showErrors: string= 'all'): Observable<ApiObject[]> {
        const resource = 'lendings';
        const stream = this.getStreamSource<ApiObject[]>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getRoot().subscribe((root) => {
                this.rest.get<ApiObject[]>(root._links.lending, token).subscribe(data => {
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            }, error => this.errorHandler(error, resource, 'GET', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    postLending(newData, showErrors: string= 'all'): Observable<ApiObject> {
        const resource = 'lendings';

        return this.currentJWT.pipe(
            mergeMap(jwt => jwt.getValidApiToken()),
            mergeMap(token => {
                return this.getRoot().pipe(
                    mergeMap(root => {
                        return this.rest.post<ApiObject>(root._links.lending, newData, token).pipe(mergeMap(data => {
                            const stream = this.getStreamSource<ApiObject>(resource + '/' + data.id);
                            this.updateResource(resource, data);
                            this.getLentItems();
                            return (stream.asObservable() as Observable<ApiObject>).pipe(filter(d => d != null));
                        }),
                        catchError(error => {
                            this.errorHandler(error, resource, 'POST', showErrors);
                            return observableThrowError(error);
                        }),
                    );
                }));
            }),
        );
    }

    getLending(id: number, showErrors: string= 'all'): Observable<ApiObject> {
        const baseResource = 'lendings';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.getRoot().subscribe((root) => {
                this.rest.get<ApiObject>(root._links.lending.href + id, token).subscribe(data => {
                    this.updateResource(baseResource, data);
                }, error => this.errorHandler(error, resource, 'GET', showErrors));
            }, error => this.errorHandler(error, resource, 'GET', showErrors));
        });

        return stream.asObservable().pipe(filter(data => data != null));
    }

    /**
     * Returns items or the whole lending.
     *
     * The returned observable evaluates to true only if the lending was deleted by the api.
     *
     * @param lending the lending to return
     * @param id a single item id to return from the lending (if unset return all items)
     * @param showErrors whether to show errors to the user
     */
    returnLending(lending: ApiObject, id?: number, showErrors: string= 'all'): Observable<boolean> {
        const baseResource = 'lendings';
        const resource = baseResource + '/' + lending.id;
        const stream = this.getStreamSource<ApiObject>(resource);

        const data = { ids: [] };

        if (id != null) {
            data.ids.push(id);
        } else {
            lending.items.forEach(item => {
                data.ids.push(item.id);
            });
        }

        const result = new AsyncSubject<boolean>();

        this.currentJWT.pipe(mergeMap(jwt => jwt.getValidApiToken())).subscribe(token => {
            this.rest.post<ApiObject>(lending, data, token).subscribe(data => {
                if (data != null) {
                    this.updateResource(baseResource, data);
                    result.next(false);
                } else {
                    // cleanup old stream
                    result.next(true);
                    this.streams[resource] = null;
                    stream.next(null);
                }
                result.complete();
                this.getLentItems();
            }, error => {
                result.error(error);
                result.complete();
                this.errorHandler(error, resource, 'GET', showErrors)
            });
        });

        return result.asObservable();
    }

}
