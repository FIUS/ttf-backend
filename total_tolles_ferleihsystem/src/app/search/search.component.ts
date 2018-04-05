import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';

import { QuestionService } from '../shared/forms/question.service';
import { QuestionControlService } from '../shared/forms/question-control.service';
import { QuestionBase } from '../shared/forms/question-base';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { TypeQuestion } from '../shared/forms/question-type';
import { NumberQuestion } from '../shared/forms/question-number';

@Component({
  selector: 'ttf-search',
  templateUrl: './search.component.html'
})
export class SearchComponent  {

    typeQuestion: NumberQuestion = new NumberQuestion();

    @Input() asSelector: boolean = false;
    @Input() selectedCallback: (any) => void = (test) => {};

    open: boolean = false;

    result: ApiObject[];

    searchstring: string = '';
    type: number;
    tags: Set<number>;

    constructor(private api: ApiService) { }

    search() {
        this.api.search(this.searchstring, this.type, this.tags).subscribe(data => this.result = data);
    }
}
