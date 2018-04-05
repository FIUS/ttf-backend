import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { StagingService } from '../navigation/staging-service';
import { ApiService } from '../shared/rest/api.service';
import { JWTService } from '../shared/rest/jwt.service';
import { Subscription } from 'rxjs/Rx';

@Component({
  selector: 'ttf-lending',
  templateUrl: './lending.component.html'
})
export class LendingComponent implements OnInit, OnDestroy {

    private paramSubscription: Subscription;
    private lendingSubscription: Subscription;

    lendingID: number;
    lending;

    constructor(private data: NavigationService, private api: ApiService,
                private jwt: JWTService, private route: ActivatedRoute) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Lending');
        this.paramSubscription = this.route.params.subscribe(params => {
            this.update(parseInt(params['id'], 10));
        });
    }

    update(lendingID: number) {
        this.lendingID = lendingID;
        if (this.lendingSubscription != null) {
            this.lendingSubscription.unsubscribe();
        }
        this.data.changeBreadcrumbs([new Breadcrumb('Lendings', '/lendings'),
            new Breadcrumb('"' + lendingID.toString() + '"', '/lendings/' + lendingID)]);
        this.lendingSubscription = this.api.getLending(lendingID).subscribe(lending => {
            if (lending == null) {
                return;
            }
            this.lending = lending;
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

}
