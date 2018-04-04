import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';

@Component({
  selector: 'ttf-item-detail',
  templateUrl: './item-detail.component.html'
})
export class ItemDetailComponent implements OnInit, OnDestroy {

    private paramSubscription: Subscription;
    private itemSubscription: Subscription;
    private attributesSubscription: Subscription;

    itemID: number;
    item;
    attributes: number[] = [];

    constructor(private data: NavigationService, private api: ApiService, private route: ActivatedRoute) { }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Item');
        this.paramSubscription = this.route.params.subscribe(params => {
            this.update(parseInt(params['id'], 10));
        });
    }

    update(itemID: number) {
        this.itemID = itemID;
        if (this.itemSubscription != null) {
            this.itemSubscription.unsubscribe();
        }
        this.data.changeBreadcrumbs([new Breadcrumb('Items', '/items'),
            new Breadcrumb('"' + itemID.toString() + '"', '/items/' + itemID)]);
        this.itemSubscription = this.api.getItem(itemID).subscribe(item => {
            if (item == null) {
                return;
            }
            this.item = item;
            this.data.changeBreadcrumbs([new Breadcrumb('Items', '/items'),
                new Breadcrumb('"' + item.name + '"', '/items/' + itemID)]);

            if (this.attributesSubscription != null) {
                this.attributesSubscription.unsubscribe();
            }
            this.attributesSubscription = this.api.getAttributes(item).subscribe(attributes => {
                const ids = [];
                attributes.forEach(attr => {
                    ids.push(attr.attribute_definition_id)
                })
                if (ids.length !== this.attributes.length) {
                    this.attributes = ids;
                } else {
                    ids.forEach((id, index) => {
                        if (this.attributes[index] !== id) {
                            this.attributes[index] = id;
                        }
                    })
                }
            })
        });
    }

    ngOnDestroy(): void {
        if (this.paramSubscription != null) {
            this.paramSubscription.unsubscribe();
        }
        if (this.itemSubscription != null) {
            this.itemSubscription.unsubscribe();
        }
        if (this.attributesSubscription != null) {
            this.attributesSubscription.unsubscribe();
        }
    }

}
