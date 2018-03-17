import { Component, OnInit, OnDestroy } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';
import { ApiObject } from '../shared/rest/api-base.service';

@Component({
  selector: 'ttf-tag-list',
  templateUrl: './tag-list.component.html'
})
export class TagListComponent implements OnInit, OnDestroy {

    filter: string = null;

    alphabet: Array<string> = ['#', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                               'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                               'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    data: Map<string, any>;

    private subscription: Subscription;

    constructor(private api: ApiService) { }

    ngOnInit(): void {
        this.subscription = this.api.getTags().subscribe(data => {
            const map = new Map<string, ApiObject[]>();
            this.alphabet.forEach(letter => map.set(letter, []));
            data.forEach(tag => {
                let letter: string = tag.name.toUpperCase().substr(0, 1);
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
                    list.push(tag);
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
