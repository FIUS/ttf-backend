
import {take} from 'rxjs/operators';
import { Component, OnChanges, Input, ViewChild, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs';
import { NumberQuestion } from '../shared/forms/question-number';
import { DynamicFormComponent } from '../shared/forms/dynamic-form/dynamic-form.component';
import { JWTService } from '../shared/rest/jwt.service';

@Component({
  selector: 'ttf-item-type-edit',
  templateUrl: './item-type-edit.component.html'
})
export class ItemTypeEditComponent implements OnChanges, OnDestroy {

    private subscription: Subscription;
    private canContainSubscription: Subscription;

    @ViewChild(DynamicFormComponent, { static: true }) form;

    typeQuestion: NumberQuestion = new NumberQuestion();

    @Input() itemTypeID: number;

    itemType: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    canContainTypeID: number;
    canContain: ApiObject[];

    constructor(private api: ApiService, private router: Router, private jwt: JWTService) { }

    ngOnChanges(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        this.subscription = this.api.getItemType(this.itemTypeID).subscribe(data => {
            this.itemType = data;
            if (this.canContainSubscription != null) {
                this.canContainSubscription.unsubscribe();
            }
            this.canContainSubscription = this.api.getContainedTypes(this.itemType).subscribe(canContain => {
                this.canContain = canContain;
            });
        });
    }

    ngOnDestroy(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        if (this.canContainSubscription != null) {
            this.canContainSubscription.unsubscribe();
        }
    }

    addCanContain() {
        if (this.canContainTypeID != null && this.canContainTypeID >= 0) {
            this.api.postContainedType(this.itemType, this.canContainTypeID);
        }
    }

    removeCanContain(id) {
        if (id != null && id >= 0) {
            this.api.deleteContainedType(this.itemType, id);
        }
    }

    save = (event) => {
        this.api.putItemType(this.itemTypeID, event).pipe(take(1)).subscribe(() => {
            this.form.saveFinished(true);
        }, () => {
            this.form.saveFinished(false);
        });
    }

    delete = () => {
        this.api.deleteItemType(this.itemType.id).pipe(take(1)).subscribe(() => this.router.navigate(['item-types']));
    }

}
