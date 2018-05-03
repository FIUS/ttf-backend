import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';

@Component({
    selector: 'ttf-search-overview',
    templateUrl: './search-overview.component.html'
})
export class SearchOverviewComponent implements OnInit {

    constructor(private data: NavigationService) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Search');
        this.data.changeBreadcrumbs([new Breadcrumb('Search', '/search')]);
    }

}
