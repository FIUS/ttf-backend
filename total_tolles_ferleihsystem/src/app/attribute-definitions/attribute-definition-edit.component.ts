import { Component, OnChanges, Input, ViewChild, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';
import { DynamicFormComponent } from '../shared/forms/dynamic-form/dynamic-form.component';
import { JWTService } from '../shared/rest/jwt.service';

@Component({
  selector: 'ttf-attribute-definition-edit',
  templateUrl: './attribute-definition-edit.component.html'
})
export class AttributeDefinitionEditComponent implements OnChanges, OnDestroy {

    private subscription: Subscription;

    @ViewChild(DynamicFormComponent) form;

    @Input() attributeDefinitionID: number;

    attrDef: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    constructor(private api: ApiService, private router: Router, private jwt: JWTService) { }

    ngOnChanges(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        this.subscription = this.api.getAttributeDefinition(this.attributeDefinitionID).subscribe(data => {
            this.attrDef = data;
        });
    }

    ngOnDestroy(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
    }

    save = (event) => {
        this.api.putAttributeDefinition(this.attrDef.id, event).take(1).subscribe(() => {
            this.form.saveFinished(true);
        }, () => {
            this.form.saveFinished(false);
        });
    }

    delete = () => {
        this.api.deleteAttributeDefinition(this.attrDef.id).take(1).subscribe(() => this.router.navigate(['attribute-definitions']));
    };

}
