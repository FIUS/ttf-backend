import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from './navigation-service';

@Component({
  selector: 'ttf-breadcrumbs',
  templateUrl: './breadcrumbs.component.html',
  styleUrls: ['./breadcrumbs.component.scss']
})
export class BreadcrumbsComponent implements OnInit {

    breadcrumbs: Array<Breadcrumb>;

    constructor(private data: NavigationService) { }

    ngOnInit(): void {
        this.data.currentBreadcrumbs.subscribe(breadcrumbs => this.breadcrumbs = breadcrumbs);
    }

}
