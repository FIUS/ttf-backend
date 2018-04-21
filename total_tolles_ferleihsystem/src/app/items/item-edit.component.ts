import { Component, OnChanges, Input, ViewChild, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';
import { DynamicFormComponent } from '../shared/forms/dynamic-form/dynamic-form.component';

@Component({
  selector: 'ttf-item-edit',
  templateUrl: './item-edit.component.html'
})
export class ItemEditComponent implements OnChanges, OnDestroy {

    private subscription: Subscription;

    @ViewChild(DynamicFormComponent) form;

    @Input() itemID: number;

    item: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    constructor(private api: ApiService, private router: Router) { }

    ngOnChanges(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        this.subscription = this.api.getItem(this.itemID).subscribe(data => {
            this.item = data;
        });
    }

    ngOnDestroy(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
    }

    save = (event) => {
        this.api.putItem(this.item.id, event).take(1).subscribe(() => {
            this.form.saveFinished(true);
        }, () => {
            this.form.saveFinished(false);
        });
    }

    delete = () => {
        this.api.deleteItem(this.item.id).take(1).subscribe(() => this.router.navigate(['items']));
    };

}
