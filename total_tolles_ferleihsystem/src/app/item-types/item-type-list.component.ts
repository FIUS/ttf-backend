import { Component, OnInit, OnDestroy } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';
import { ApiObject } from '../shared/rest/api-base.service';

@Component({
  selector: 'ttf-item-type-list',
  templateUrl: './item-type-list.component.html'
})
export class ItemTypeListComponent implements OnInit, OnDestroy {

    filter: string = null;

    alphabet: Array<string> = ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                               'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                               'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    data: Map<string, any>;

    private subscription: Subscription;

    constructor(private api: ApiService) { }

    ngOnInit(): void {
        this.subscription = this.api.getItemTypes().subscribe(data => {
            const map = new Map<string, ApiObject[]>();
            this.alphabet.forEach(letter => map.set(letter, []));
            data.forEach(itemType => {
                let letter: string = itemType.name.toUpperCase().substr(0, 1);
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
                    letter = '0';
                }
                const list = map.get(letter);
                if (list != null) {
                    list.push(itemType);
                }
            });
            this.data = map;
        });
    }

    ngOnDestroy(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
    }

    setFilter(value) {
        if (value == null || this.data != null && this.data.get(value) != null && this.data.get(value).length > 0) {
            this.filter = value;
        }
    }

}
