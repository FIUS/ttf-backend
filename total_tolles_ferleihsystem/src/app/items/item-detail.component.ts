import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Subscription } from 'rxjs/Rx';

import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { StagingService } from '../navigation/staging-service';
import { ApiService } from '../shared/rest/api.service';
import { JWTService } from '../shared/rest/jwt.service';
import { ApiObject } from '../shared/rest/api-base.service';

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

    edit: boolean = false;

    itemID: number;
    item: ApiObject;
    attributes: ApiObject[];
    tags: ApiObject[];
    attributeIDs: number[] = [];

    canContain: ApiObject[];
    containedItems: ApiObject[];
    containedItemsAsMap: Map<number, ApiObject[]> = new Map<number, ApiObject[]>();
    chooseItemType: number = -1;

    fileIDs: ApiObject[] = [];

    dragover: boolean = false;
    filesUploading: string[] = [];
    filesUploadingMap: Map<string, any> = new Map();
    filenameMap: Map<number, string> = new Map();

    constructor(private data: NavigationService, private api: ApiService,
                private jwt: JWTService, private staging: StagingService,
                private route: ActivatedRoute) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Item');
        this.paramSubscription = this.route.params.subscribe(params => {
            this.update(parseInt(params['id'], 10));
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
                const ids = [];
                attributes.forEach(attr => {
                    ids.push(attr.attribute_definition_id)
                })
                if (ids.length !== this.attributeIDs.length) {
                    this.attributeIDs = ids;
                } else {
                    ids.forEach((id, index) => {
                        if (this.attributeIDs[index] !== id) {
                            this.attributeIDs[index] = id;
                        }
                    })
                }
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

    get lendingDuration() {
        if (this.item != null && this.item.lending_duration >= 0) {
            return this.item.lending_duration;
        }
        if (this.tags != null) {
            let duration;
            this.tags.forEach(tag => {
                if (tag.lending_duration >= 0 && (duration == null || duration > tag.lending_duration)) {
                    duration = tag.lending_duration;
                }
            });
            if (duration != null) {
                return duration;
            }
        }
        if (this.item != null && this.item.type != null) {
            return this.item.type.lending_duration;
        }
    }

    get canEdit() {
        return this.jwt.isModerator() || this.jwt.isAdmin();
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

}
