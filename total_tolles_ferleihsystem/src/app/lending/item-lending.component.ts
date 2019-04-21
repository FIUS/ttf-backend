import { Component, OnInit, OnDestroy, Input, Output, EventEmitter } from '@angular/core';
import { Subscription } from 'rxjs/Rx';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';

@Component({
  selector: 'ttf-item-lending',
  templateUrl: './item-lending.component.html'
})
export class ItemLendingComponent implements OnInit, OnDestroy {


    @Input() item: any;
    @Output() return: EventEmitter<number> = new EventEmitter<number>();

    tags: ApiObject[] = [];
    attributes: ApiObject[] = [];

    open: boolean = false;


    constructor(private api: ApiService) { }

    ngOnInit(): void {
      if (this.item != null && this.item != null) {
            this.api.getTagsForItem(this.item).take(1).subscribe(tags => {
              this.tags = tags;
            });
            this.api.getAttributes(this.item).take(1).subscribe(attributes => {
              this.attributes = attributes;
            });
        }
    }

    ngOnDestroy(): void {
    }
}
