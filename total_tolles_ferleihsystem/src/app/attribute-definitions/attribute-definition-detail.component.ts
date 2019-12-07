import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'ttf-attribute-definition-detail',
  templateUrl: './attribute-definition-detail.component.html'
})
export class AttributeDefinitionDetailComponent implements OnInit, OnDestroy {

    private paramSubscription: Subscription;
    private attrDefSubscription: Subscription;

    attributeDefinitionID: number;

    constructor(private data: NavigationService, private api: ApiService, private route: ActivatedRoute) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Attribute Definition');
        this.paramSubscription = this.route.params.subscribe(params => {
            this.update(parseInt(params['id'], 10));
        });
    }

    update(attrDefID: number) {
        this.attributeDefinitionID = attrDefID;
        if (this.attrDefSubscription != null) {
            this.attrDefSubscription.unsubscribe();
        }
        this.data.changeBreadcrumbs([new Breadcrumb('Attribute Definitions', '/attribute-definitions'),
            new Breadcrumb('"' + attrDefID.toString() + '"', '/attribute-definitions/' + attrDefID)]);
        this.attrDefSubscription = this.api.getAttributeDefinition(attrDefID).subscribe(attrDef => {
            this.data.changeBreadcrumbs([new Breadcrumb('Attribute Definitions', '/attribute-definitions'),
                new Breadcrumb('"' + attrDef.name + '"', '/attribute-definitions/' + attrDefID)]);
        });
    }

    ngOnDestroy(): void {
        if (this.paramSubscription != null) {
            this.paramSubscription.unsubscribe();
        }
        if (this.attrDefSubscription != null) {
            this.attrDefSubscription.unsubscribe();
        }
    }

}
