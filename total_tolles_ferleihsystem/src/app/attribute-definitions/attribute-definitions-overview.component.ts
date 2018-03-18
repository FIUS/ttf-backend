import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';

@Component({
  selector: 'ttf-attribute-definitions-overview',
  templateUrl: './attribute-definitions-overview.component.html'
})
export class AttributeDefinitionsOverviewComponent implements OnInit {

    private newAttributeDefinitionData;

    constructor(private data: NavigationService, private api: ApiService) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – AttributeDefinitions');
        this.data.changeBreadcrumbs([new Breadcrumb('AttributeDefinitions', '/attribute-definitions')]);
    }

    onDataChange(data) {
        this.newAttributeDefinitionData = data;
    }

    save = (() => {
        this.api.postAttributeDefinition(this.newAttributeDefinitionData).subscribe();
    }).bind(this);

}
