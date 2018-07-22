import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';
import { JWTService } from '../shared/rest/jwt.service';

@Component({
  selector: 'ttf-item-type-detail',
  templateUrl: './item-type-detail.component.html'
})
export class ItemTypeDetailComponent implements OnInit, OnDestroy {

    private paramSubscription: Subscription;
    private itemTypeSubscription: Subscription;

    itemTypeID: number;
    itemType;

    constructor(private data: NavigationService, private api: ApiService, private route: ActivatedRoute, private jwt: JWTService) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – ItemType');
        this.paramSubscription = this.route.params.subscribe(params => {
            this.update(parseInt(params['id'], 10));
        });
    }

    update(typeID: number) {
        this.itemTypeID = typeID;
        if (this.itemTypeSubscription != null) {
            this.itemTypeSubscription.unsubscribe();
        }
        this.data.changeBreadcrumbs([new Breadcrumb('ItemTypes', '/item-types'),
            new Breadcrumb('"' + typeID.toString() + '"', '/item-types/' + typeID)]);
        this.itemTypeSubscription = this.api.getItemType(typeID).subscribe(itemType => {
            this.itemType = itemType;
            this.data.changeBreadcrumbs([new Breadcrumb('ItemTypes', '/item-types'),
                new Breadcrumb('"' + itemType.name + '"', '/item-types/' + typeID)]);
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
