
import {take} from 'rxjs/operators';
import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { JWTService } from '../shared/rest/jwt.service';
import { SettingsService } from '../shared/settings/settings.service';
import { Router } from '@angular/router';

@Component({
  selector: 'ttf-items-overview',
  templateUrl: './items-overview.component.html'
})
export class ItemsOverviewComponent implements OnInit {

    private newItemData;

    constructor(private data: NavigationService, private api: ApiService,
                private jwt: JWTService, private settings: SettingsService,
                private router: Router) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Items');
        this.data.changeBreadcrumbs([new Breadcrumb('Items', '/items')]);
    }

    onDataChange(data) {
        this.newItemData = data;
    }

    save = () => {
        const sub = this.api.postItem(this.newItemData).subscribe(data => {
            this.settings.getSetting('navigateAfterCreation').pipe(take(1)).subscribe(navigate => {
                if (navigate) {
                    this.router.navigate(['items', data.id]);
                }
                sub.unsubscribe();
            });
        });
    };

}
