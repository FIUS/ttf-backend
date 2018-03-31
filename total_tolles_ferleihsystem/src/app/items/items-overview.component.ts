import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';

@Component({
  selector: 'ttf-items-overview',
  templateUrl: './items-overview.component.html'
})
export class ItemsOverviewComponent implements OnInit {

    private newItemData;

    constructor(private data: NavigationService, private api: ApiService) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Items');
        this.data.changeBreadcrumbs([new Breadcrumb('Items', '/items')]);
    }

    onDataChange(data) {
        this.newItemData = data;
    }

    save = (() => {
        this.api.postItem(this.newItemData).subscribe();
    }).bind(this);

}
