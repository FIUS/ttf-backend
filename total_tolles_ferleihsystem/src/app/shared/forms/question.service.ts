import { Injectable, OnInit } from '@angular/core';
import { Observable } from 'rxjs/Rx';
import { AsyncSubject } from 'rxjs/AsyncSubject';

import { ApiService } from '../rest/api.service';

import { QuestionBase, QuestionOptions } from './question-base';
import { HiddenQuestion } from './question-hidden';
import { StringQuestion } from './question-string';
import { TextQuestion } from './question-text';
import { DateQuestion } from './question-date';
import { DateTimeQuestion } from './question-datetime';
import { NumberQuestion } from './question-number';
import { DurationQuestion } from './question-duration';
import { DropdownQuestion } from './question-dropdown';
import { BooleanQuestion } from './question-boolean';
import { TypeQuestion } from './question-type';

import { Options } from 'selenium-webdriver';

@Injectable()
export class QuestionService implements OnInit {

    private swagger: Observable<any>;

    private observables: {
        [propName: string]: AsyncSubject<QuestionBase<any>[]>;
    } = {};

    constructor(private api: ApiService) { }

    ngOnInit(): void {
        this.swagger = this.api.getSpec();
    }

    getQuestions = (model: string): Observable<QuestionBase<any>[]> => {
        if (this.swagger == undefined) {
            this.swagger = this.api.getSpec();
        }

        return this.swagger.flatMap(spec => {
            if (spec == undefined) {
                return Observable.of([]);
            }

            if (this.observables[model] == undefined) {
                this.observables[model] = new AsyncSubject<QuestionBase<any>[]>();
            }

            this.parseModel(spec, model);

            return this.observables[model].asObservable();
        })

    }

    getQuestionsFromScheme = (scheme: object): Observable<QuestionBase<any>[]> => {
        if (this.swagger == undefined) {
            this.swagger = this.api.getSpec();
        }

        return this.swagger.flatMap(spec => {
            if (spec == undefined) {
                return Observable.of([]);
            }

            const result = new AsyncSubject<QuestionBase<any>[]>();

            const questionOptions = new Map<string, QuestionOptions>()
            const model = this.parseJsonSchemeModel(scheme, spec, questionOptions);
            const questionsArray: QuestionBase<any>[] = [];
            questionOptions.forEach(options => questionsArray.push(this.getQuestion(options)));
            result.next(questionsArray.sort((a, b) => a.order - b.order));
            result.complete();

            return result;
        });

    }

    private parseModel(spec: any, modelID: string, questionOptions?: Map<string, QuestionOptions>, orderMultiplier: number = 1) {
        let recursionStart = false;
        if (questionOptions == null) {
            questionOptions = new Map<string, QuestionOptions>();
            recursionStart = true;
        }

        let re = /^.*\//;
        modelID = modelID.replace(re, '');

        let model = spec.definitions[modelID];

        model = this.parseJsonSchemeModel(model, spec, questionOptions);

        if (recursionStart) {
            let questionsArray: QuestionBase<any>[] = [];
            questionOptions.forEach(options => questionsArray.push(this.getQuestion(options)));
            this.observables[modelID].next(questionsArray.sort((a, b) => a.order - b.order));
            this.observables[modelID].complete();
        }
    }

    private parseJsonSchemeModel(model: any, spec: any, questionOptions: Map<string, QuestionOptions>, orderMultiplier: number = 1) {
        if (model != null) {
            if (model.allOf != null) {
                let tempModel;
                for (const parent of model.allOf) {
                    if (parent.$ref != null) {
                        this.parseModel(spec, parent.$ref, questionOptions, orderMultiplier);
                    }
                    if (parent.properties != null) {
                        tempModel = parent;
                    }
                    orderMultiplier *= 100;
                }
                model = tempModel;
            }
            if (model.properties != null) {
                for (const propID in model.properties) {
                    this.updateOptions(questionOptions, propID, model, orderMultiplier);
                }
            }
        }
        return model;
    }

    private updateOptions(questionOptions: Map<string, QuestionOptions>, propID: string, model: any, orderMultiplier: number = 1) {
        let options: QuestionOptions = questionOptions.get(propID);
        if (options == null) {
            options = {
                key: propID,
                label: propID,
                order: questionOptions.size,
            };
        }
        let prop = model.properties[propID];
        if (model.required != null) {
            for (let name of model.required) {
                if (name === propID) {
                    options.required = true;
                }
            }
        }
        options.valueType = prop.type;
        if (prop['x-valueType'] != null) {
            options.valueType = prop['x-valueType'];
        }
        options.controlType = prop.type;
        if (prop.format != null) {
            options.controlType = prop.format;
        }
        if (prop.title != null) {
            options.label = prop.title;
        }
        if (prop.description != null) {
            options.description = prop.description;
        }

        options.readOnly = !!prop.readOnly;
        if (prop.example != null) {
            options.value = prop.example;
        }
        if (prop.enum != null) {
            options.options = prop.enum;
        }

        if (prop.minLength != null) {
            options.min = prop.minLength;
        }
        if (prop.maxLength != null) {
            options.max = prop.maxLength;
        }

        if (prop.pattern != null) {
            options.pattern = prop.pattern;
        }

        if (prop.minimum != null) {
            options.min = prop.minimum;
        }
        if (prop.maximum != null) {
            options.max = prop.maximum;
        }

        if (prop['x-order'] != null) {
            options.order = prop['x-order'] * orderMultiplier;
        }
        if (prop['x-nullable'] != null) {
            options.nullable = prop['x-nullable'];
        }
        if (prop['x-nullValue'] != null) {
            options.nullValue = prop['x-nullValue'];
        }

        questionOptions.set(propID, options);
    }

    private getQuestion(options: QuestionOptions): QuestionBase<any> {
        if (options.options != null) {
            return new DropdownQuestion(options);
        }
        if (options.controlType === 'date') {
            return new DateQuestion(options);
        }
        if (options.controlType === 'date-time') {
            return new DateTimeQuestion(options);
        }
        if (options.controlType === 'boolean') {
            return new BooleanQuestion(options);
        }
        if (options.controlType === 'integer') {
            if (options.key.toUpperCase().includes('TYPE_ID')) {
                return new TypeQuestion(options);
            }
            if (options.key.toUpperCase().includes('DURATION')) {
                return new DurationQuestion(options);
            }
            return new NumberQuestion(options);
        }
        if (options.controlType === 'number') {
            return new NumberQuestion(options);
        }
        if (options.controlType === 'string') {
            if (options.pattern != null || options.max != null) {
                return new StringQuestion(options);
            } else {
                return new TextQuestion(options);
            }
        }
        if (options.readOnly) {
            return new HiddenQuestion(options);
        }
        return new QuestionBase(options);
    }

}
