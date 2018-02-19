import { Injectable } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';

import { QuestionBase } from './question-base';

@Injectable()
export class QuestionControlService {
    constructor() { }

    toFormGroup(questions: QuestionBase<any>[]) {
        let group: any = {};

        questions.forEach(question => {
            let validators = [];
            if (question.required) {
                if (question.controlType === 'boolean') {
                    // nothing
                } else if (question.controlType === 'string' || question.controlType === 'text') {
                    if (question.min != undefined && question.min === 1) {
                        validators.push(Validators.required);
                    }
                } else {
                    validators.push(Validators.required);
                }
            }
            if (question.min != undefined) {
                if (question.controlType === 'number') {
                    validators.push(Validators.min(question.min as number));
                }
                if (question.controlType === 'string' || question.controlType === 'text') {
                    if (question.min > 1) {
                        validators.push(Validators.minLength(question.min as number))
                    }
                }
            }
            if (question.max != undefined) {
                if (question.controlType === 'number') {
                    validators.push(Validators.max(question.max as number));
                }
                if (question.controlType === 'string' || question.controlType === 'text') {
                    validators.push(Validators.maxLength(question.max as number))
                }
            }

            if (validators.length > 1) {
                const validator = Validators.compose(validators);
                group[question.key] = new FormControl(question.value || '', validator)
            } else if (validators.length === 1) {
                group[question.key] = new FormControl(question.value || '', validators[0])
            } else {
                group[question.key] = new FormControl(question.value || '');
            }
        });
        return new FormGroup(group);
    }
}
