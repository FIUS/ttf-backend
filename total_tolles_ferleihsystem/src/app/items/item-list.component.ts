import { Component, OnInit, OnDestroy, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { Subscription, Subject } from 'rxjs/Rx';

import { StagingService } from '../navigation/staging-service';

import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { JWTService } from '../shared/rest/jwt.service';

@Component({
  selector: 'ttf-item-list',
  templateUrl: './item-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ItemListComponent implements OnInit, OnDestroy {

    filter: string = null;

    alphabet: Array<string> = ['#', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                               'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                               'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    data: Map<string, ApiObject[]>;
    itemTypes: Map<number, ApiObject> = new Map<number, ApiObject>();
    itemTags: Map<number, ApiObject[]> = new Map<number, ApiObject[]>();
    itemAttributes: Map<number, ApiObject[]> = new Map<number, ApiObject[]>();
    deleted: ApiObject[];

    private changeDetectionBatchSubject: Subject<null> = new Subject<null>();

    private subscription: Subscription;
    private deletedSubscription: Subscription;

    constructor(private api: ApiService, private jwt: JWTService,
        private staging: StagingService, private changeDetector: ChangeDetectorRef) { }

    private runChangeDetection() {
        this.changeDetector.markForCheck();
        //this.changeDetector.checkNoChanges();
    }

    ngOnInit(): void {
        this.changeDetectionBatchSubject.asObservable().debounceTime(100).subscribe(() => this.runChangeDetection());
        this.api.getItemTypes() // refresh cached itemTypes
        this.subscription = this.api.getItems().subscribe(data => {
            const map = new Map<string, ApiObject[]>();
            this.alphabet.forEach(letter => map.set(letter, []));
            data.forEach(item => {
                let letter: string = item.name.toUpperCase().substr(0, 1);
                if (letter === 'Ä') {
                    letter = 'A';
                }
                if (letter === 'Ö') {
                    letter = 'O';
                }
                if (letter === 'Ü') {
                    letter = 'U';
                }
                if (letter === 'ẞ') {
                    letter = 'S';
                }
                if (letter.match(/^[A-Z]/) == null) {
                    letter = '#';
                }
                const list = map.get(letter);
                if (list != null) {
                    list.push(item);
                }
            });
            this.data = map;
            this.changeDetectionBatchSubject.next();
        });
        if (this.jwt.isAdmin()) {
            this.deletedSubscription = this.api.getItems(true).subscribe(data => {
                this.deleted = data;
                this.changeDetectionBatchSubject.next();
            });
        }
    }

    ngOnDestroy(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        if (this.deletedSubscription != null) {
            this.deletedSubscription.unsubscribe();
        }
    }

    setFilter(value) {
        if (value == null || value === 'DELETED' && this.deleted != null && this.deleted.length > 0
            || this.data != null && this.data.get(value) != null && this.data.get(value).length > 0) {
            this.filter = value;
            this.changeDetectionBatchSubject.next();
        }
    }

    /**
     * Load further data for items in view.
     *
     * @param item the item that was scrolled into view
     */
    loadData(item) {
        this.api.getItemType(item.type_id, 'all', true).take(1).subscribe(itemType => {
            this.itemTypes.set(itemType.id, itemType);
            this.changeDetectionBatchSubject.next();
        });
        this.api.getTagsForItem(item, 'errors', true).take(1).subscribe(tags => {
            this.itemTags.set(item.id, tags);
            this.changeDetectionBatchSubject.next();
        });
        this.api.getAttributes(item, 'errors', true).take(1).subscribe(attributes => {
            this.itemAttributes.set(item.id, attributes);
            this.changeDetectionBatchSubject.next();
        });
    }

}
