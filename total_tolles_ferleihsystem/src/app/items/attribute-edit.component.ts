import { Component, OnChanges, Input, OnDestroy, SimpleChanges } from '@angular/core';
import { Router } from '@angular/router';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';

@Component({
  selector: 'ttf-attribute-edit',
  templateUrl: './attribute-edit.component.html'
})
export class AttributeEditComponent implements OnChanges, OnDestroy {

    private itemSubscription: Subscription;
    private attributeSubscription: Subscription;

    @Input() itemID: number;
    @Input() attributeID: number;

    item: ApiObject;
    attribute: ApiObject;

    constructor(private api: ApiService, private router: Router) { }

    ngOnChanges(changes: SimpleChanges): void {
        if (this.itemSubscription != null) {
            this.itemSubscription.unsubscribe();
        }
        if (this.itemID != null) {
            this.itemSubscription = this.api.getItem(this.itemID).subscribe(data => {
                this.item = data;
                if (this.item != null) {
                    if (this.attributeSubscription != null) {
                        this.attributeSubscription.unsubscribe();
                    }
                    if (this.attributeID != null) {
                        this.attributeSubscription = this.api.getAttribute(this.item, this.attributeID).subscribe(data => {
                            this.attribute = data;
                        });
                    }
                }
            });
        }
    }

    ngOnDestroy(): void {
        if (this.itemSubscription != null) {
            this.itemSubscription.unsubscribe();
        }
        if (this.attributeSubscription != null) {
            this.attributeSubscription.unsubscribe();
        }
    }

}
