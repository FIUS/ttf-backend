import { Component, Input, Output, OnInit, OnChanges, SimpleChanges, EventEmitter } from '@angular/core';
import { FormGroup } from '@angular/forms';

import { QuestionBase } from '../question-base';
import { QuestionService } from '../question.service';
import { QuestionControlService } from '../question-control.service';

import { ApiObject } from '../../rest/api-base.service';

@Component({
    selector: 'dynamic-form',
    templateUrl: './dynamic-form.component.html',
    providers: [QuestionControlService]
})
export class DynamicFormComponent implements OnInit, OnChanges {

    @Input() objectModel: string;
    @Input() startValues: ApiObject = {_links:{self:{href:''}}};

    questions: QuestionBase<any>[] = [];
    customNull: {[propName: string]: any} = {};
    form: FormGroup;

    @Output() valid: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() data: EventEmitter<any> = new EventEmitter<any>();

    constructor(private qcs: QuestionControlService, private qs: QuestionService) { }

    update() {
        this.qs.getQuestions(this.objectModel).subscribe(questions => {
            this.questions = questions;
            this.customNull = {};
            for (let question of this.questions) {
                if (question.nullValue != undefined) {
                    this.customNull[question.key] = question.nullValue;
                }
            }
            this.form = this.qcs.toFormGroup(this.questions);
            this.form.statusChanges.subscribe(status => {
                this.valid.emit(this.form.valid);
                let patched = {};
                for (let key in this.form.value) {
                    if (this.form.value[key] != null && this.form.value[key] != '') {
                        patched[key] = this.form.value[key];
                    } else {
                        patched[key] = this.customNull[key];
                    }
                }
                this.data.emit(patched);
            });
            this.patchFormValues();
        });
    }

    patchFormValues() {
        let patched = {};
        for (let key in this.startValues) {
            if (this.customNull[key] !== this.startValues[key]) {
                patched[key] = this.startValues[key];
            } else {
                patched[key] = null;
            }
        }
        if (this.form != undefined) {
            this.form.patchValue(patched);
        }
    }

    ngOnInit() {
        this.update();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.objectType != undefined) {
            this.update();
        } else {
            if (this.form != undefined && changes.startValues != undefined) {
                this.patchFormValues();
            }
        }
    }
}
