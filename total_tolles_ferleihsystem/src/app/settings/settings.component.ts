import { Component, OnInit } from '@angular/core';

import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { SettingsService } from '../shared/settings/settings.service';

import { Themes } from './themes';
import { ApiService } from 'app/shared/rest/api.service';

@Component({
  selector: 'ttf-settings',
  templateUrl: './settings.component.html'
})
export class SettingsComponent implements OnInit {

    rememberEditMode: boolean;
    navigateAfterCreation: boolean;
    theme: any = {};
    themeId: number = 0;
    infoTimeout: number = -1;
    alertTimeout: number = -1;
    errorTimeout: number = -1;
    pinnedTypes: number[] = [];

    itemTypes = [];

    constructor(private data: NavigationService, private settings: SettingsService, private api: ApiService) { }

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
                this.theme = Themes[0];
            }
        });
        this.settings.getSetting('infoTimeout').subscribe(timeout => {
            if (timeout == null) {
                timeout = 5000;
            }
            this.infoTimeout = timeout;
        });
        this.settings.getSetting('alertTimeout').subscribe(timeout => {
            if (timeout == null) {
                timeout = 15000;
            }
            this.alertTimeout = timeout;
        });
        this.settings.getSetting('errorTimeout').subscribe(timeout => {
            if (timeout == null) {
                timeout = -1;
            }
            this.errorTimeout = timeout;
        });
        this.settings.getSetting('pinnedItemTypes').subscribe(pinnedTypes => {
            if (pinnedTypes == null) {
                pinnedTypes = [];
            }
            this.pinnedTypes = pinnedTypes;
        });
        this.api.getItemTypes().subscribe(itemTypes => this.itemTypes = itemTypes);
    }

    isTypePinned(type) {
        return this.pinnedTypes.some(typeId => type.id === typeId);
    }

    toggleType(type) {
        if (this.isTypePinned(type)) {
            this.settings.setSetting('pinnedItemTypes', this.pinnedTypes.filter(typeId => typeId !== type.id));
        } else {
            this.pinnedTypes.push(type.id);
            this.settings.setSetting('pinnedItemTypes', this.pinnedTypes);
        }
    }

    changeColor() {
        this.themeId = (this.themeId + 1) % Themes.length;
        this.theme = Themes[this.themeId];
        this.settings.setSetting('theme', this.theme);
    }

}
