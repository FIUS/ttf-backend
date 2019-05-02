import { Component, ViewChild, Input } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { myDialogComponent } from '../shared/dialog/dialog.component';
import { ApiService } from '../shared/rest/api.service';
import { SettingsService } from '../shared/settings/settings.service';
import { Router } from '@angular/router';

@Component({
  selector: 'ttf-attribute-definition-create',
  templateUrl: './attribute-definition-create.component.html'
})
export class AttributeDefinitionCreateComponent {

    @Input() allowAutoNavigate: boolean = false;

    @ViewChild(myDialogComponent) dialog: myDialogComponent;

    private newAttributeDefinitionData;

    constructor(private api: ApiService, private settings: SettingsService,
                private router: Router) { }

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
                        data.jsonschema = JSON.stringify(json, undefined, '\t');
                    } catch (error) {}
                }
            }
        }
        this.newAttributeDefinitionData = data;
    }

    save = () => {
        const sub = this.api.postAttributeDefinition(this.newAttributeDefinitionData).subscribe(data => {
            if (this.allowAutoNavigate) {
                this.settings.getSetting('navigateAfterCreation').take(1).subscribe(navigate => {
                    console.log(navigate)
                    if (navigate) {
                        this.router.navigate(['attribute-definitions', data.id]);
                    }
                    sub.unsubscribe();
                });
            }
        });
    };

}
