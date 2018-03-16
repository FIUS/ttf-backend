import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';

@Component({
  selector: 'ttf-item-types-overview',
  templateUrl: './item-types-overview.component.html'
})
export class ItemTypesOverviewComponent implements OnInit {

    private newItemTypeData;

    constructor(private data: NavigationService, private api: ApiService) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – ItemTypes');
        this.data.changeBreadcrumbs([new Breadcrumb('ItemTypes', '/item-types')]);
    }

    onDataChange(data) {
        this.newItemTypeData = data;
    }

    save = (() => {
        this.api.postItemType(this.newItemTypeData).subscribe();
    }).bind(this);

}
