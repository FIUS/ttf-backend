import { Component, ViewChild } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { myDialogComponent } from '../shared/dialog/dialog.component';
import { ApiService } from '../shared/rest/api.service';

@Component({
  selector: 'ttf-attribute-definition-create',
  templateUrl: './attribute-definition-create.component.html'
})
export class AttributeDefinitionCreateComponent {

    @ViewChild(myDialogComponent) dialog: myDialogComponent;

    private newAttributeDefinitionData;

    constructor(private api: ApiService) { }

    open() {
        this.dialog.open();
    }

    onDataChange(data) {
        this.newAttributeDefinitionData = data;
    }

    save = (() => {
        this.api.postAttributeDefinition(this.newAttributeDefinitionData).subscribe();
    }).bind(this);

}
