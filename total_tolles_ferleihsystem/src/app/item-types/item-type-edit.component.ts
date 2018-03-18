import { Component, OnChanges, Input } from '@angular/core';
import { Router } from '@angular/router';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';

@Component({
  selector: 'ttf-item-type-edit',
  templateUrl: './item-type-edit.component.html'
})
export class ItemTypeEditComponent implements OnChanges {

    private subscription: Subscription;

    @Input() itemTypeID: number;

    itemType: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    valid: boolean = false;
    data: any = {};

    constructor(private api: ApiService, private router: Router) { }

    ngOnChanges(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        this.subscription = this.api.getItemType(this.itemTypeID).subscribe(data => {
            this.itemType = data;
        });
    }

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.data = data;
    }

    save(event) {
        if (this.valid) {
            this.api.putItemType(this.itemType.id, this.data);
        }
    }

    delete = (() => {
        this.api.deleteItemType(this.itemType.id).take(1).subscribe(() => this.router.navigate(['item-types']));
    }).bind(this);

}
