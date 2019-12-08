
import {timer as observableTimer,  Subscription, Observable } from 'rxjs';

import {take} from 'rxjs/operators';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { StagingService } from '../navigation/staging-service';
import { ApiService } from '../shared/rest/api.service';
import { JWTService } from '../shared/rest/jwt.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { SettingsService } from '../shared/settings/settings.service';


@Component({
  selector: 'ttf-item-detail',
  templateUrl: './item-detail.component.html'
})
export class ItemDetailComponent implements OnInit, OnDestroy {

    private paramSubscription: Subscription;
    private itemSubscription: Subscription;
    private itemTypeSubscription: Subscription;
    private attributesSubscription: Subscription;
    private tagsSubscription: Subscription;
    private containedTypeSubscription: Subscription;
    private containedItemsSubscription: Subscription;
    private parentItemsSubscription: Subscription;
    private filesSubscription: Subscription;

    rememberEditMode: boolean = false;
    editMode: boolean = false;
    _edit: boolean = false;

    itemID: number;
    item: ApiObject;
    itemType: ApiObject;
    attributes: ApiObject[];
    tags: ApiObject[];

    parentItems: ApiObject[];
    canContain: ApiObject[];
    containedItems: ApiObject[];
    containedItemsAsMap: Map<number, ApiObject[]> = new Map<number, ApiObject[]>();
    chooseItemType: number = -1;

    fileIDs: ApiObject[] = [];

    dragover: boolean = false;
    filesUploading: string[] = [];
    filesUploadingMap: Map<string, any> = new Map();
    filenameMap: Map<number, string> = new Map();

    newItemData: any;

    constructor(private data: NavigationService, private api: ApiService,
                private jwt: JWTService, private staging: StagingService,
                private route: ActivatedRoute, private settings: SettingsService,
                private router: Router) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Item');
        this.paramSubscription = this.route.params.subscribe(params => {
            this.update(parseInt(params['id'], 10));
        });
        this.settings.getSetting('rememberEditMode').subscribe(rememberEditMode => {
            this.rememberEditMode = rememberEditMode;
        });
        this.settings.getSetting('editMode').subscribe(editMode => {
            if (this.rememberEditMode) {
                this.editMode = editMode;
            }
        });
    }

    update(itemID: number) {
        if (this.itemID !== itemID) { // cleanup values from previous item
            this.item = null;
            this.attributes = [];
            this.tags= [];

            this.canContain = [];
            this.containedItems = [];
            this.containedItemsAsMap = new Map<number, ApiObject[]>();
            this.chooseItemType = -1;

            this.fileIDs = [];

            this.filesUploading = [];
            this.filesUploadingMap = new Map();
            this.filenameMap = new Map();

            this.newItemData = new Object();
        }
        this.itemID = itemID;
        if (this.itemSubscription != null) {
            this.itemSubscription.unsubscribe();
        }
        this.data.changeBreadcrumbs([new Breadcrumb('Items', '/items'),
        new Breadcrumb('"' + itemID.toString() + '"', '/items/' + itemID)]);
        this.itemSubscription = this.api.getItem(itemID).subscribe(item => {
            if (item == null) {
                return;
            }
            this.item = item;
            if (this.itemType == null || this.itemType.id !== item.type_id) {
                if (this.itemTypeSubscription != null) {
                    this.itemTypeSubscription.unsubscribe();
                }
                this.itemTypeSubscription = this.api.getItemType(item.type_id).subscribe(itemType => {
                    this.itemType = itemType;
                    this.updateContainedItems(item, itemType);
                    this.updateParentItems(item);
                });
            }
            this.data.changeBreadcrumbs([new Breadcrumb('Items', '/items'),
            new Breadcrumb('"' + item.name + '"', '/items/' + itemID)]);

            if (this.attributesSubscription != null) {
                this.attributesSubscription.unsubscribe();
            }
            this.attributesSubscription = this.api.getAttributes(item).subscribe(attributes => {
                this.attributes = attributes;
            });
            if (this.tagsSubscription != null) {
                this.tagsSubscription.unsubscribe();
            }
            this.tagsSubscription = this.api.getTagsForItem(item).subscribe(tags => {
                this.tags = tags;
            });
            if (this.filesSubscription != null) {
                this.filesSubscription.unsubscribe();
            }
            this.filesSubscription = this.api.getFiles(item).subscribe(files => {
                const ids = [];
                const nameMap = new Map();
                files.forEach(file => {
                    ids.push(file.id);
                    nameMap.set(file.id, file.name);
                });
                ids.sort((a, b) => {
                    if (nameMap.get(a) > nameMap.get(b)) {
                        return -1;
                    } else if (nameMap.get(a) === nameMap.get(b)) {
                        return 0;
                    } else {
                        return 1;
                    }
                });
                for (let i = 0; i < ids.length && i < this.fileIDs.length; i++) {
                    if (this.fileIDs[i] !== ids[i]) {
                        this.fileIDs[i] = ids[i];
                    }
                }
                if (ids.length < this.fileIDs.length) {
                    this.fileIDs.splice(ids.length, this.fileIDs.length - ids.length);
                }
                if (ids.length > this.fileIDs.length) {
                    for (let i = this.fileIDs.length; i < ids.length; i++) {
                        this.fileIDs.push(ids[i]);
                    }
                }
            })
        });
    }

    private updateParentItems(item: ApiObject) {
        if (this.parentItemsSubscription != null) {
            this.parentItemsSubscription.unsubscribe();
        }
        this.parentItemsSubscription = this.api.getParentItems(item).subscribe(parents => {
            this.parentItems = parents;
        });
    }

    private updateContainedItems(item: ApiObject, itemType: ApiObject) {
        if (this.containedTypeSubscription != null) {
            this.containedTypeSubscription.unsubscribe();
        }
        this.containedTypeSubscription = this.api.getContainedTypes(itemType).subscribe(canContain => {
            this.canContain = canContain;
        });
        if (this.containedItemsSubscription != null) {
            this.containedItemsSubscription.unsubscribe();
        }
        this.containedItemsSubscription = this.api.getContainedItems(item).subscribe(containedItems => {
            const itemMap = new Map<number, ApiObject[]>();
            containedItems.forEach(innerItem => {
                let list = itemMap.get(innerItem.type_id);
                if (list == null) {
                    list = [];
                    itemMap.set(innerItem.type_id, list);
                }
                list.push(innerItem);
            });
            this.containedItemsAsMap = itemMap;
            this.containedItems = containedItems;
        });
    }

    get canEdit() {
        return this.jwt.isAdmin();
    }

    get edit() {
        if (this.rememberEditMode) {
            return this.editMode;
        }
        return this._edit;
    }

    set edit(value: boolean) {
        this._edit = value;
        if (this.rememberEditMode) {
            this.settings.setSetting('editMode', value);
        }
    }

    attributeTrackFn(index: any, attr: any) {
        return attr.attribute_definition_id;
    }

    ngOnDestroy(): void {
        if (this.paramSubscription != null) {
            this.paramSubscription.unsubscribe();
        }
        if (this.itemSubscription != null) {
            this.itemSubscription.unsubscribe();
        }
        if (this.itemTypeSubscription != null) {
            this.itemTypeSubscription.unsubscribe();
        }
        if (this.attributesSubscription != null) {
            this.attributesSubscription.unsubscribe();
        }
        if (this.tagsSubscription != null) {
            this.tagsSubscription.unsubscribe();
        }
        if (this.containedTypeSubscription != null) {
            this.containedTypeSubscription.unsubscribe();
        }
        if (this.containedItemsSubscription != null) {
            this.containedItemsSubscription.unsubscribe();
        }
        if (this.parentItemsSubscription != null) {
            this.parentItemsSubscription.unsubscribe();
        }
        if (this.filesSubscription != null) {
            this.filesSubscription.unsubscribe();
        }
    }

    addItemToContained = (item: ApiObject, parent?: ApiObject) => {
        if (parent == null) {
            parent = this.item;
        }
        this.api.postContainedItem(parent, item.id);
    }

    removeItemFromContained(item: ApiObject, parent?: ApiObject) {
        if (parent == null) {
            parent = this.item;
        }
        this.api.deleteContainedItem(parent, item.id);
    }

    upload(file: File) {
        this.filesUploading.push(file.name);
        this.filesUploadingMap.set(file.name, file);
        this.api.uploadFile(this.item, file).subscribe(data => {
            const index = this.filesUploading.findIndex(name => name === file.name);
            if (index >= 0) {
                this.filesUploading.splice(index, 1);
            }
            this.filenameMap.set(data.id, file.name);
            this.filesUploadingMap.delete(file.name);
            this.api.getFiles(this.item);
        });
    }

    onDataChange(data) {
        this.newItemData = data;
    }

    save = () => {
        const sub = this.api.postItem(this.newItemData).pipe(take(1)).subscribe(data => {
            this.settings.getSetting('navigateAfterCreation').pipe(take(1)).subscribe(navigate => {
                this.addItemToContained(data, this.item);
                if (navigate) {
                    observableTimer(150).pipe(take(1)).subscribe(() => {
                        this.router.navigate(['items', data.id]);
                    });
                }
                sub.unsubscribe();
            });
        });
    };

}
