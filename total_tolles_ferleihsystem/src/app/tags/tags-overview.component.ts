
import {take} from 'rxjs/operators';
import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { JWTService } from '../shared/rest/jwt.service';
import { SettingsService } from '../shared/settings/settings.service';
import { Router } from '@angular/router';

@Component({
  selector: 'ttf-tags-overview',
  templateUrl: './tags-overview.component.html'
})
export class TagsOverviewComponent implements OnInit {

    private newTagData;

    constructor(private data: NavigationService, private api: ApiService,
                private jwt: JWTService, private settings: SettingsService,
                private router: Router) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Tags');
        this.data.changeBreadcrumbs([new Breadcrumb('Tags', '/tags')]);
    }

    onDataChange(data) {
        this.newTagData = data;
    }

    save = () => {
        const sub = this.api.postTag(this.newTagData).subscribe(data => {
            this.settings.getSetting('navigateAfterCreation').pipe(take(1)).subscribe(navigate => {
                if (navigate) {
                    this.router.navigate(['tags', data.id]);
                }
                sub.unsubscribe();
            });
        });
    };

}
