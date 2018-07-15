import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { Subscription } from 'rxjs/Rx';

import { StagingService } from '../navigation/staging-service';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';

@Component({
  selector: 'ttf-staged-item',
  templateUrl: './staged-item.component.html'
})
export class StagedItemComponent implements OnInit, OnDestroy {

    private itemSubscription: Subscription;
    private tagsSubscription: Subscription;
    private attributesSubscription: Subscription;

    @Input() itemID: number;

    item: ApiObject;
    tags: ApiObject[];
    attributes: ApiObject[];

    open: boolean = false;


    constructor(private staging: StagingService, private api: ApiService) { }

    ngOnInit(): void {
        this.itemSubscription = this.api.getItem(this.itemID).subscribe(item => {
            this.item = item;
            this.tagsSubscription = this.api.getTagsForItem(item).subscribe(tags => this.tags = tags);
            this.attributesSubscription = this.api.getAttributes(item).subscribe(attributes => this.attributes = attributes);
        });
    }

    ngOnDestroy(): void {
        if (this.itemSubscription != null) {
            this.itemSubscription.unsubscribe();
        }
        if (this.tagsSubscription != null) {
            this.tagsSubscription.unsubscribe();
        }
        if (this.attributesSubscription != null) {
            this.attributesSubscription.unsubscribe();
        }
    }

}
