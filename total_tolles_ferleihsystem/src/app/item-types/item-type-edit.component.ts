import { Component, OnChanges, Input } from '@angular/core';
import { Router } from '@angular/router';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';
import { NumberQuestion } from '../shared/forms/question-number';

@Component({
  selector: 'ttf-item-type-edit',
  templateUrl: './item-type-edit.component.html'
})
export class ItemTypeEditComponent implements OnChanges {

    private subscription: Subscription;
    private canContainSubscription: Subscription;

    typeQuestion: NumberQuestion = new NumberQuestion();

    @Input() itemTypeID: number;

    itemType: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    valid: boolean = false;
    data: any = {};

    canContainTypeID: number;
    canContain: ApiObject[];

    constructor(private api: ApiService, private router: Router) { }

    ngOnChanges(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        this.subscription = this.api.getItemType(this.itemTypeID).subscribe(data => {
            this.itemType = data;
            if (this.canContainSubscription != null) {
                this.canContainSubscription.unsubscribe();
            }
            this.canContainSubscription = this.api.getCanContain(this.itemType).subscribe(canContain => {
                this.canContain = canContain;
            });
        });
    }

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.data = data;
    }

    addCanContain() {
        if (this.canContainTypeID != null && this.canContainTypeID >= 0) {
            this.api.postCanContain(this.itemType, this.canContainTypeID);
        }
    }

    removeCanContain(id) {
        if (this.canContainTypeID != null && this.canContainTypeID >= 0) {
            this.api.deleteCanContain(this.itemType, id);
        }
    }

    delete = () => {
        this.api.deleteItemType(this.itemType.id).take(1).subscribe(() => this.router.navigate(['item-types']));
    }

}
