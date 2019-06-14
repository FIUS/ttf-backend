import { Component, OnInit, OnDestroy } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';

@Component({
  selector: 'ttf-items-of-type-overview',
  templateUrl: './items-of-type-overview.component.html'
})
export class ItemsOfTypeOverviewComponent implements OnInit, OnDestroy {

    itemType;
    itemTypeId;

    private paramSubscription: Subscription;
    private itemTypeSubscription: Subscription;

    constructor(private data: NavigationService, private api: ApiService, private route: ActivatedRoute) { }

    ngOnInit(): void {
        this.paramSubscription = this.route.params.subscribe(params => {
            const newId = parseInt(params['id'], 10);
            if (this.itemTypeId !== newId) {
                this.itemTypeId = newId;
                if (this.itemTypeSubscription != null) {
                    this.itemTypeSubscription.unsubscribe();
                }
                this.itemTypeSubscription = this.api.getItemType(this.itemTypeId).subscribe(itemType => {
                    this.itemType = itemType;
                    this.data.changeTitle('Total Tolles Ferleihsystem – Items ' + itemType.name);
                    this.data.changeBreadcrumbs([new Breadcrumb('Items for Type "' + itemType.name + '"',
                        '/items-of-type/' + this.itemTypeId)]);
                });
            }
        });
    }

    ngOnDestroy(): void {
        if (this.paramSubscription != null) {
            this.paramSubscription.unsubscribe();
        }
        if (this.itemTypeSubscription != null) {
            this.itemTypeSubscription.unsubscribe();
        }
    }

}
