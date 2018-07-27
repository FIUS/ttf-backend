import { Component, OnInit } from '@angular/core';

import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { SettingsService } from '../shared/settings/settings.service';

@Component({
  selector: 'ttf-settings',
  templateUrl: './settings.component.html'
})
export class SettingsComponent implements OnInit {

    rememberEditMode: boolean;
    navigateAfterCreation: boolean;
    theme: any = {};

    constructor(private data: NavigationService, private settings: SettingsService) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Settings');
        this.data.changeBreadcrumbs([new Breadcrumb('Settings', '/settings')]);
        this.settings.getSetting('rememberEditMode').subscribe(editMode => {
            this.rememberEditMode = editMode;
        });
        this.settings.getSetting('navigateAfterCreation').subscribe(navigate => {
            this.navigateAfterCreation = navigate;
        });
        this.settings.getSetting('theme').subscribe(theme => {
            if (theme != null) {
                this.theme = theme;
            } else {
                this.theme = new Object();
            }
        });
    }

    changeColor() {
        if (this.theme.backgroundColor == null || this.theme.backgroundColor == 'white') {
            this.theme.backgroundColor = 'red';
        } else if (this.theme.backgroundColor == 'red') {
            this.theme.backgroundColor = 'blue';
        } else if (this.theme.backgroundColor == 'blue') {
            this.theme.backgroundColor = 'green';
        } else if (this.theme.backgroundColor == 'green') {
            this.theme.backgroundColor = 'white';
        }
        this.settings.setSetting('theme', this.theme);
    }

}
