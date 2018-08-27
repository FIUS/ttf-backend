import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { Subscription } from 'rxjs/Rx';

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
    private attributesSubscription: Subscription;
    private tagsSubscription: Subscription;
    private containedTypeSubscription: Subscription;
    private containedItemsSubscription: Subscription;
    private filesSubscription: Subscription;

    rememberEditMode: boolean = false;
    editMode: boolean = false;
    _edit: boolean = false;

    itemID: number;
    item: ApiObject;
    attributes: ApiObject[];
    tags: ApiObject[];

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
            if (this.containedTypeSubscription != null) {
                this.containedTypeSubscription.unsubscribe();
            }
            this.containedTypeSubscription = this.api.getCanContain(item.type).subscribe(canContain => {
                this.canContain = canContain;
            });
            if (this.containedItemsSubscription != null) {
                this.containedItemsSubscription.unsubscribe();
            }
            this.containedItemsSubscription = this.api.getContainedItems(item).subscribe(containedItems => {
                const itemMap = new Map<number, ApiObject[]>();
                containedItems.forEach(item => {
                    let list = itemMap.get(item.type.id);
                    if (list == null) {
                        list = [];
                        itemMap.set(item.type.id, list);
                    }
                    list.push(item);
                });
                this.containedItemsAsMap = itemMap;
                this.containedItems = containedItems;
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
        if (this.filesSubscription != null) {
            this.filesSubscription.unsubscribe();
        }
    }

    addItemToContained = (item: ApiObject) => {
        this.api.postContainedItem(this.item, item.id);
    }

    removeItemFromContained(item: ApiObject) {
        this.api.deleteContainedItem(this.item, item.id);
    }

    upload(file: File) {
        this.filesUploading.push(file.name);
        this.filesUploadingMap.set(file.name, file);
        this.api.uploadFile(this.item, file).subscribe(data => {
            console.log(data);
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
        this.api.postItem(this.newItemData).subscribe(data => {
            this.settings.getSetting('navigateAfterCreation').take(1).subscribe(navigate => {
                this.addItemToContained(data);
                if (navigate) {
                    this.router.navigate(['items', data.id]);
                }
            });
        });
    };

}
