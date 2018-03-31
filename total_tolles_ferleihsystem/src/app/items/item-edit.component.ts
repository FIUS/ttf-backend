import { Component, OnChanges, Input } from '@angular/core';
import { Router } from '@angular/router';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';

@Component({
  selector: 'ttf-item-edit',
  templateUrl: './item-edit.component.html'
})
export class ItemEditComponent implements OnChanges {

    private subscription: Subscription;

    @Input() itemID: number;

    item: ApiObject = {
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
        this.subscription = this.api.getItem(this.itemID).subscribe(data => {
            this.item = data;
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
            this.api.putItem(this.item.id, this.data);
        }
    }

    delete = (() => {
        this.api.deleteItem(this.item.id).take(1).subscribe(() => this.router.navigate(['items']));
    }).bind(this);

}
