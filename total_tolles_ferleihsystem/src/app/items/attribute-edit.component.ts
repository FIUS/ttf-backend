import { Component, OnChanges, Input } from '@angular/core';
import { Router } from '@angular/router';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';

@Component({
  selector: 'ttf-attribute-edit',
  templateUrl: './attribute-edit.component.html'
})
export class AttributeEditComponent implements OnChanges {

    private itemSubscription: Subscription;
    private attributeSubscription: Subscription;

    @Input() itemID: number;
    @Input() attributeID: number;

    item: ApiObject;
    attribute: ApiObject;

    constructor(private api: ApiService, private router: Router) { }

    ngOnChanges(): void {
        if (this.itemSubscription != null) {
            this.itemSubscription.unsubscribe();
        }
        this.itemSubscription = this.api.getItem(this.itemID).subscribe(data => {
            this.item = data;
            if (this.item != null) {
                if (this.attributeSubscription != null) {
                    this.attributeSubscription.unsubscribe();
                }
                this.attributeSubscription = this.api.getAttribute(this.item, this.attributeID).subscribe(data => {
                    this.attribute = data;
                });
            }
        });
    }

}
