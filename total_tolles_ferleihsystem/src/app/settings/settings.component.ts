import { Component, OnInit } from '@angular/core';

import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { SettingsService } from '../shared/settings/settings.service';

import * as themes from '../../assets/themes.json';

@Component({
  selector: 'ttf-settings',
  templateUrl: './settings.component.html'
})
export class SettingsComponent implements OnInit {

    rememberEditMode: boolean;
    navigateAfterCreation: boolean;
    theme: any = {};
    themeId: number = 0;

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
                this.theme = themes['data'][0];
            }
        });
    }

    changeColor() {
        this.themeId = (this.themeId + 1) % themes['count'];
        this.theme = themes['data'][this.themeId];
        this.settings.setSetting('theme', this.theme);
    }

}
