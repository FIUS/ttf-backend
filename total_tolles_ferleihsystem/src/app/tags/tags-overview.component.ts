import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { JWTService } from '../shared/rest/jwt.service';

@Component({
  selector: 'ttf-tags-overview',
  templateUrl: './tags-overview.component.html'
})
export class TagsOverviewComponent implements OnInit {

    private newTagData;

    constructor(private data: NavigationService, private api: ApiService, private jwt: JWTService) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Tags');
        this.data.changeBreadcrumbs([new Breadcrumb('Tags', '/tags')]);
    }

    onDataChange(data) {
        this.newTagData = data;
    }

    save = (() => {
        this.api.postTag(this.newTagData).subscribe();
    }).bind(this);

}
