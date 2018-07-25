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
    }

}
