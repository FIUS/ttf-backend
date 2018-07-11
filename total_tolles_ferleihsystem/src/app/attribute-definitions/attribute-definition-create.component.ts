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
                const maxLength = (window as any).maxDBStringLength - 2;
                if (data.jsonschema == null || data.jsonschema === '') {
                    data.jsonschema = JSON.stringify({maxLength: maxLength}, undefined, '\t');
                } else {
                    try {
                        const json = JSON.parse(data.jsonschema);
                        if (json.maxLength == null || json.maxLength > maxLength) {
                            json.maxLength = maxLength;
                        }
                        data.jsonschema = JSON.stringify({maxLength: maxLength}, undefined, '\t');
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
