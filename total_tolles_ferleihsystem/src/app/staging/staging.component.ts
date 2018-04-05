import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { StagingService } from '../navigation/staging-service';
import { ApiService } from '../shared/rest/api.service';

@Component({
  selector: 'ttf-staging',
  templateUrl: './staging.component.html'
})
export class StagingComponent implements OnInit {


    constructor(private data: NavigationService, private api: ApiService, private staging: StagingService) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Staging');
        this.data.changeBreadcrumbs([new Breadcrumb('Staging', '/staging')]);
    }

}
