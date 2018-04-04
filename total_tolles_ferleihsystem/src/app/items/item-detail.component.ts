import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { JWTService } from '../shared/rest/jwt.service';
import { Subscription } from 'rxjs/Rx';

@Component({
  selector: 'ttf-item-detail',
  templateUrl: './item-detail.component.html'
})
export class ItemDetailComponent implements OnInit, OnDestroy {

    private paramSubscription: Subscription;
    private itemSubscription: Subscription;
    private attributesSubscription: Subscription;
    private tagsSubscription: Subscription;

    edit: boolean = false;

    itemID: number;
    item;
    attributes;
    tags;
    attributeIDs: number[] = [];

    constructor(private data: NavigationService, private api: ApiService,
                private jwt: JWTService, private route: ActivatedRoute) { }

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
                this.attributes = attributes;
                const ids = [];
                attributes.forEach(attr => {
                    ids.push(attr.attribute_definition_id)
                })
                if (ids.length !== this.attributeIDs.length) {
                    this.attributeIDs = ids;
                } else {
                    ids.forEach((id, index) => {
                        if (this.attributeIDs[index] !== id) {
                            this.attributeIDs[index] = id;
                        }
                    })
                }
            });
            if (this.tagsSubscription != null) {
                this.tagsSubscription.unsubscribe();
            }
            this.tagsSubscription = this.api.getTagsForItem(item).subscribe(tags => {
                this.tags = tags;
            })
        });
    }

    get lendingDuration() {
        if (this.item != null && this.item.lending_duration >= 0) {
            return this.item.lending_duration;
        }
        if (this.tags != null) {
            let duration;
            this.tags.forEach(tag => {
                if (tag.lending_duration >= 0 && (duration == null || duration > tag.lending_duration)) {
                    duration = tag.lending_duration;
                }
            });
            if (duration != null) {
                return duration;
            }
        }
        if (this.item != null && this.item.type != null) {
            return this.item.type.lending_duration;
        }
    }

    get canEdit() {
        return this.jwt.isModerator() || this.jwt.isAdmin();
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
        if (this.tagsSubscription != null) {
            this.tagsSubscription.unsubscribe();
        }
    }

}
