import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';

import { QuestionService } from '../shared/forms/question.service';
import { QuestionControlService } from '../shared/forms/question-control.service';
import { QuestionBase } from '../shared/forms/question-base';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { TypeQuestion } from '../shared/forms/question-type';
import { NumberQuestion } from '../shared/forms/question-number';
import { StagingService } from '../navigation/staging-service';

@Component({
  selector: 'ttf-search',
  templateUrl: './search.component.html'
})
export class SearchComponent  {

    typeQuestion: NumberQuestion = new NumberQuestion();


    open: boolean = false;

    searchstring: string = '';
    type: number;
    tags: Set<number>;

    searchDone: boolean = false;

    alphabet: Array<string> = ['#', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                               'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                               'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    data: Map<string, any>;
    result: ApiObject[];

    filter: string;

    @Input() asSelector: boolean = false;
    @Input() selectedCallback: (any) => void = (test) => {};


    constructor(private api: ApiService, private staging: StagingService) { }

    search() {
        this.searchDone = false;
        this.api.search(this.searchstring, this.type, this.tags).subscribe(data => {
            const map = new Map<string, ApiObject[]>();
            this.alphabet.forEach(letter => map.set(letter, []));
            data.forEach(item => {
                let letter: string = item.name.toUpperCase().substr(0, 1);
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
                    list.push(item);
                }
            });
            this.data = map;
            this.searchDone = true;
            console.log('HI');
        });
    }

    setFilter(value) {
        if (this.data != null && this.data.get(value) != null && this.data.get(value).length > 0) {
            this.filter = value;
        }
    }
}
