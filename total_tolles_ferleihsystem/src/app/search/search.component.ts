import { Component, OnInit, OnDestroy, Input, Output, EventEmitter } from '@angular/core';
import { FormGroup } from '@angular/forms';

import { QuestionService } from '../shared/forms/question.service';
import { QuestionControlService } from '../shared/forms/question-control.service';
import { QuestionBase } from '../shared/forms/question-base';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { TypeQuestion } from '../shared/forms/question-type';
import { NumberQuestion } from '../shared/forms/question-number';
import { StagingService } from '../navigation/staging-service';
import { Subject, Observable, AsyncSubject } from 'rxjs/Rx';

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
    attributes: ApiObject[];
    attributeQuestions: Map<number, QuestionBase<any>[]> = new Map<number, QuestionBase<any>[]>();
    attributeForms: Map<number, FormGroup> = new Map<number, FormGroup>();

    searchDone: boolean = false;

    alphabet: Array<string> = ['#', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                               'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                               'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    data: Map<string, any>;
    result: ApiObject[];

    filter: string;

    @Input() asSelector: boolean = false;
    @Input() restrictToType: number = -1;
    @Output() selectedChanged: EventEmitter<ApiObject> = new EventEmitter<ApiObject>();

    constructor(private api: ApiService, private staging: StagingService,
                private qs: QuestionService, private qcs: QuestionControlService) { }

    resetSearchData() {
        console.log('RESET');
        this.searchDone = false;
        this.data = new Map<string, ApiObject[]>();
    }

    search() {
        this.searchDone = false;
        if (this.restrictToType != null && this.restrictToType >= 0) {
            this.type = this.restrictToType;
        }
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
        });
    }

    setFilter(value) {
        if (this.data != null && this.data.get(value) != null && this.data.get(value).length > 0) {
            this.filter = value;
        }
    }

    updateAttributes() {
        const typeAndTagsSubject = new Subject<ApiObject>();

        typeAndTagsSubject.flatMap(typeOrTag => {
            return this.api.getLinkedAttributeDefinitions(typeOrTag).take(1)
        }).map(attributes => Observable.from(attributes))
        .concatAll()
        .distinct(attr => attr.id)
        .toArray()
        .map(attrs => attrs.sort((a, b) => a.type.localeCompare(b.type)).sort((a, b) => a.name.localeCompare(b.name)))
        .subscribe(data => this.attributes = data);

        const finished = [];
        if (this.type >= 0) {
            const obs = this.api.getItemType(this.type).take(1);
            obs.subscribe(itemType => {
                typeAndTagsSubject.next(itemType);
            });
            finished.push(obs);
        }
        if (this.tags != null ) {
            this.tags.forEach(tagID => {
                const obs = this.api.getTag(tagID).take(1);
                obs.subscribe(itemTag => {
                    typeAndTagsSubject.next(itemTag);
                });
                finished.push(obs);
            });
        }
        Observable.forkJoin(finished).subscribe(() => typeAndTagsSubject.complete());
    }

    getQuestion(attribute_definition) {
        let schema: any = {};
        if (attribute_definition.jsonschema != null && attribute_definition.jsonschema !== '') {
            schema = JSON.parse(attribute_definition.jsonschema);
        }
        schema.type = attribute_definition.type;
        this.qs.getQuestionsFromScheme({
            type: 'object',
            properties: {
                [attribute_definition.name]: schema,
            }
        }).take(1).subscribe(questions => {
            this.attributeQuestions.set(attribute_definition.id, questions);
            const form = this.qcs.toFormGroup(questions)
            this.attributeForms.set(attribute_definition.id, form);
            let value = undefined; // TODO
            try {
                value = JSON.parse(value);
            } catch (SyntaxError) {}
            form.patchValue({
                [attribute_definition.name]: value,
            });
        });
    }

    select(item: ApiObject) {
        this.selectedChanged.emit(item);
    }
}
