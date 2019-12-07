
import {take} from 'rxjs/operators';
import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { JWTService } from '../shared/rest/jwt.service';
import { SettingsService } from '../shared/settings/settings.service';
import { Router } from '@angular/router';

@Component({
  selector: 'ttf-item-types-overview',
  templateUrl: './item-types-overview.component.html'
})
export class ItemTypesOverviewComponent implements OnInit {

    private newItemTypeData;

    constructor(private data: NavigationService, private api: ApiService,
                private jwt: JWTService, private settings: SettingsService,
                private router: Router) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – ItemTypes');
        this.data.changeBreadcrumbs([new Breadcrumb('ItemTypes', '/item-types')]);
    }

    onDataChange(data) {
        this.newItemTypeData = data;
    }

    save = () => {
        const sub = this.api.postItemType(this.newItemTypeData).subscribe(data => {
            this.settings.getSetting('navigateAfterCreation').pipe(take(1)).subscribe(navigate => {
                if (navigate) {
                    this.router.navigate(['item-types', data.id]);
                }
                sub.unsubscribe();
            });
        });
    };

}
