import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { Router } from '@angular/router';
import { ApiService } from '../shared/rest/api.service';
import { JWTService } from '../shared/rest/jwt.service';

@Component({
  selector: 'ttf-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

    constructor(private data: NavigationService, private api: ApiService,
        private jwt: JWTService, private router: Router) { }

    ngOnInit(): void {
        if (this.jwt.loggedIn()) {
            this.router.navigate(['/']);
        }
        this.data.changeTitle('Total Tolles Ferleihsystem – Login');
        this.data.changeBreadcrumbs([]);
    }

    login() {
        this.api.login('mod', 'mod');
    }

}
