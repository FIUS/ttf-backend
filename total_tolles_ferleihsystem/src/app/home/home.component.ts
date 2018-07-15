import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { JWTService } from '../shared/rest/jwt.service';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';

@Component({
  selector: 'ttf-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

    lentItems: ApiObject[];

    constructor(private data: NavigationService, private jwt: JWTService, private api: ApiService) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Home');
        this.data.changeBreadcrumbs([]);
        this.api.getLentItems().subscribe(items => {
            this.lentItems = items;
        })
    }

}
