import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Subscription } from 'rxjs/Rx';

import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { StagingService } from '../navigation/staging-service';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { JWTService } from '../shared/rest/jwt.service';

@Component({
  selector: 'ttf-lending-overview',
  templateUrl: './lending-overview.component.html'
})
export class LendingOverviewComponent implements OnInit, OnDestroy {

    private paramSubscription: Subscription;
    private lendingSubscription: Subscription;

    filter: string = null;

    alphabet: Array<string> = ['#', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                               'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                               'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    data: Map<string, any>;
    deleted: any[];


    constructor(private navigation: NavigationService, private api: ApiService,
                private jwt: JWTService, private route: ActivatedRoute) { }

    ngOnInit(): void {
        this.navigation.changeTitle('Total Tolles Ferleihsystem – Lending');
        this.navigation.changeBreadcrumbs([new Breadcrumb('Lendings', '/lendings')]);
        this.lendingSubscription = this.api.getLendings().subscribe(data => {
            const map = new Map<string, ApiObject[]>();
            this.alphabet.forEach(letter => map.set(letter, []));
            data.forEach(lending => {
                console.log(lending)
                let letter: string = lending.user.toUpperCase().substr(0, 1);
                if (letter === 'Ä') {
                    letter = 'A';
                }
                if (letter === 'Ö') {
                    letter = 'O';
                }
                if (letter === 'Ü') {
                    letter = 'U';
                }
                if (letter === 'ẞ') {
                    letter = 'S';
                }
                if (letter.match(/^[A-Z]/) == null) {
                    letter = '#';
                }
                const list = map.get(letter);
                if (list != null) {
                    list.push(lending);
                }
            });
            this.data = map;
        });
    }

    ngOnDestroy(): void {
        if (this.paramSubscription != null) {
            this.paramSubscription.unsubscribe();
        }
        if (this.lendingSubscription != null) {
            this.lendingSubscription.unsubscribe();
        }
    }

    setFilter(value) {
        if (this.data != null && this.data.get(value) != null && this.data.get(value).length > 0) {
            this.filter = value;
        }
    }

}
