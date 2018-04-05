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

    @Input() itemID: number;

    item: ApiObject;


    constructor(private staging: StagingService, private api: ApiService) { }

    ngOnInit(): void {
        this.itemSubscription = this.api.getItem(this.itemID).subscribe(item => this.item = item);
    }

    ngOnDestroy(): void {
        if (this.itemSubscription != null) {
            this.itemSubscription.unsubscribe();
        }
    }

}
