import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';

@Component({
  selector: 'ttf-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

    constructor(private data: NavigationService, private api: ApiService) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Login');
        this.data.changeBreadcrumbs([]);
    }

    login() {
        this.api.login('mod', 'mod');
    }

}
