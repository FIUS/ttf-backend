import { Component, OnChanges, Input } from '@angular/core';
import { Router } from '@angular/router';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';

@Component({
  selector: 'ttf-attribute-definition-edit',
  templateUrl: './attribute-definition-edit.component.html'
})
export class AttributeDefinitionEditComponent implements OnChanges {

    private subscription: Subscription;

    @Input() attributeDefinitionID: number;

    attrDef: ApiObject = {
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
        this.subscription = this.api.getAttributeDefinition(this.attributeDefinitionID).subscribe(data => {
            this.attrDef = data;
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
            this.api.putAttributeDefinition(this.attrDef.id, this.data);
        }
    }

    delete = (() => {
        this.api.deleteAttributeDefinition(this.attrDef.id).take(1).subscribe(() => this.router.navigate(['attribute-definitions']));
    }).bind(this);

}
