import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';

@Component({
  selector: 'ttf-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

    constructor(private data: NavigationService) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Home');
        this.data.changeBreadcrumbs([]);
    }

}
