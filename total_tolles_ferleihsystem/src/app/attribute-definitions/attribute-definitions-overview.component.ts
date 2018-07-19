import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { JWTService } from '../shared/rest/jwt.service';

@Component({
  selector: 'ttf-attribute-definitions-overview',
  templateUrl: './attribute-definitions-overview.component.html'
})
export class AttributeDefinitionsOverviewComponent implements OnInit {

    constructor(private data: NavigationService, private jwt: JWTService) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – AttributeDefinitions');
        this.data.changeBreadcrumbs([new Breadcrumb('AttributeDefinitions', '/attribute-definitions')]);
    }

}
