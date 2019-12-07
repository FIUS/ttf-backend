import { Component, OnInit, OnDestroy, OnChanges, Input } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs';
import { ApiObject } from '../shared/rest/api-base.service';
import { JWTService } from '../shared/rest/jwt.service';

@Component({
  selector: 'ttf-linked-attribute-definitions',
  templateUrl: './linked-attribute-definitions.component.html'
})
export class LinkedAttributeDefinitionComponent implements OnInit, OnDestroy, OnChanges {

    @Input() linkedObject: ApiObject;

    filter: string = null;

    alphabet: Array<string> = ['#', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                               'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                               'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    data: Map<string, any>;

    selected: Set<number> = new Set<number>();

    private subscription: Subscription;
    private linkedAttrDefsSubscription: Subscription;

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
    }

    ngOnChanges() {
        if (this.linkedObject != null) {
            if (this.linkedAttrDefsSubscription != null) {
                this.linkedAttrDefsSubscription.unsubscribe();
            }
            this.api.getLinkedAttributeDefinitions(this.linkedObject).subscribe(this.updateSelected);
        }
    }

    updateSelected = attrDefinitions => {
        const selected = new Set<number>();
        attrDefinitions.forEach(attrDef => {
            selected.add(attrDef.id);
        });
        this.selected = selected;
    }

    ngOnDestroy(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        if (this.linkedAttrDefsSubscription != null) {
            this.linkedAttrDefsSubscription.unsubscribe();
        }
    }

    setFilter(value) {
        if (value == null || this.data != null && this.data.get(value) != null && this.data.get(value).length > 0) {
            this.filter = value;
        }
    }

    select(attrDef) {
        if (!this.jwt.isAdmin()) {
            return;
        }
        if (this.linkedObject != null) {
            if (this.selected.has(attrDef.id)) {
                this.api.unlinkAttributeDefinition(this.linkedObject, attrDef).subscribe(this.updateSelected);
            } else {
                this.api.linkAttributeDefinition(this.linkedObject, attrDef).subscribe(this.updateSelected);
            }
        }
    }

}
