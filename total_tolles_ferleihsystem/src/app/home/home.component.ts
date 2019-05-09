import { Component, OnInit, ViewChild } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { JWTService } from '../shared/rest/jwt.service';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { Observable } from 'rxjs';
import { SettingsService } from 'app/shared/settings/settings.service';

@Component({
    selector: 'ttf-home',
    templateUrl: './home.component.html',
    styles: [
        `.ttf-button-grid {
            display: -ms-grid;
            display: grid;
            grid-template-rows: auto;
            grid-column-gap: 20px;
            grid-row-gap: 20px;
            grid-template-columns: repeat(auto-fill, 17rem);
            justify-content: space-between;
            margin-left: .5rem;
            margin-right: .5rem;
        }`
    ]
})
export class HomeComponent implements OnInit {

    lentItems: ApiObject[];
    itemTypes: Map<number, ApiObject> = new Map<number, ApiObject>();
    pinnedTypes: number[] = [];

    constructor(private data: NavigationService, private jwt: JWTService, private api: ApiService, private settings: SettingsService) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Home');
        this.data.changeBreadcrumbs([]);
        this.api.getLentItems('errors').take(2).subscribe(items => {
            this.lentItems = items;
        });
        this.api.getItemTypes().take(2).subscribe(types => {
            types.forEach(itemType => this.itemTypes.set(itemType.id, itemType));
        });
        this.settings.getSetting('pinnedItemTypes').take(2).subscribe(pinnedTypes => {
            if (pinnedTypes != null) {
                this.pinnedTypes = pinnedTypes;
            }
        });
        Observable.timer(5 * 60 * 1000, 5 * 60 * 1000).subscribe(() => this.api.getLentItems());
    }

    itemOverdue(item: ApiObject): boolean {
        const due = new Date(item.due * 1000);
        return due < new Date();
    }

}
