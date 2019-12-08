
import {timer as observableTimer,  Observable, Subscription } from 'rxjs';

import {take} from 'rxjs/operators';
import { Component, OnInit, ViewChild, OnDestroy } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { JWTService } from '../shared/rest/jwt.service';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { SettingsService } from 'app/shared/settings/settings.service';

@Component({
    selector: 'ttf-lent-items-overview',
    templateUrl: './lent-items-overview.component.html',
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
export class LentItemsOverviewComponent implements OnInit, OnDestroy {

    lentItemsSubscription: Subscription;
    lentItems: ApiObject[];
    itemTypes: Map<number, Observable<ApiObject>> = new Map<number, Observable<ApiObject>>();
    lendings: Map<number, Observable<ApiObject>> = new Map<number, Observable<ApiObject>>();

    constructor(private jwt: JWTService, private api: ApiService, private settings: SettingsService) { }

    ngOnInit(): void {
        this.lentItemsSubscription = this.api.getLentItems('errors').pipe().subscribe(items => {
            items.forEach(item => {
                if (item.type_id != null && !this.itemTypes.has(item.type_id)) {
                    this.itemTypes.set(item.type_id, this.api.getItemType(item.type_id, 'errors', true));
                }
                if (this.canSeeLending() && item.lending_id != null && !this.lendings.has(item.lending_id)) {
                    this.lendings.set(item.lending_id, this.api.getLending(item.lending_id, 'errors'));
                }
            });
            this.lentItems = items;
        });
        observableTimer(5 * 60 * 1000, 5 * 60 * 1000).subscribe(() => this.api.getLentItems());
    }

    ngOnDestroy(): void {
        if (this.lentItemsSubscription != null) {
            this.lentItemsSubscription.unsubscribe();
        }
    }

    itemOverdue(item: ApiObject): boolean {
        const due = new Date(item.due * 1000);
        return due < new Date();
    }

    canSeeLending() {
        return this.jwt.isModerator() || this.jwt.isAdmin();
    }

}
