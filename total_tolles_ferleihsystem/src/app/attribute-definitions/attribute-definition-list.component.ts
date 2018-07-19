import { Component, OnInit, OnDestroy } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';
import { ApiObject } from '../shared/rest/api-base.service';
import { JWTService } from '../shared/rest/jwt.service';

@Component({
  selector: 'ttf-attribute-definition-list',
  templateUrl: './attribute-definition-list.component.html'
})
export class AttributeDefinitionListComponent implements OnInit, OnDestroy {

    filter: string = null;

    alphabet: Array<string> = ['#', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                               'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                               'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    data: Map<string, any>;
    deleted: any[];

    private subscription: Subscription;
    private deletedSubscription: Subscription;

    constructor(private api: ApiService, private jwt: JWTService) { }

    ngOnInit(): void {
        this.subscription = this.api.getAttributeDefinitions().subscribe(data => {
            const map = new Map<string, ApiObject[]>();
            this.alphabet.forEach(letter => map.set(letter, []));
            data.forEach(attrDef => {
                let letter: string = attrDef.name.toUpperCase().substr(0, 1);
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
                    list.push(attrDef);
                }
            });
            this.data = map;
        });
        if (this.jwt.isAdmin()) {
            this.deletedSubscription = this.api.getAttributeDefinitions(true).subscribe(data => {
                this.deleted = data;
            });
        }
    }

    ngOnDestroy(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        if (this.deletedSubscription != null) {
            this.deletedSubscription.unsubscribe();
        }
    }

    setFilter(value) {
        if (value == null || value === 'DELETED' && this.deleted != null && this.deleted.length > 0
            || this.data != null && this.data.get(value) != null && this.data.get(value).length > 0) {
            this.filter = value;
        }
    }

}
