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
        if (data != null && data.type != null) {
            if (data.type === 'string') {
                if (data.jsonschema == null || data.jsonschema === '') {
                    data.jsonschema = JSON.stringify({maxLength: 253}, undefined, '\t');
                } else {
                    try {
                        const json = JSON.parse(data.jsonschema);
                        if (json.maxLength == null || json.maxLength > 253) {
                            json.maxLength = 253;
                        }
                        data.jsonschema = JSON.stringify({maxLength: 253}, undefined, '\t');
                    } catch (error) {}
                }
            }
        }
        this.newAttributeDefinitionData = data;
    }

    save = () => {
        this.api.postAttributeDefinition(this.newAttributeDefinitionData).subscribe();
    };

}
