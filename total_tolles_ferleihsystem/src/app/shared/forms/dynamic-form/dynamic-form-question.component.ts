import { Component, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';

import { QuestionBase } from '../question-base';

@Component({
    selector: 'df-question',
    templateUrl: './dynamic-form-question.component.html'
})
export class DynamicFormQuestionComponent {

    @Input() question: QuestionBase<any>;
    @Input() form: FormGroup;

    get isValid() { return this.form.controls[this.question.key].valid; }

    get error() {
        if (this.form.controls[this.question.key].valid) {
            return '';
        }
        const errors = this.form.controls[this.question.key].errors;
        if (errors) {
            if (errors.maxlength) {
                return 'Only '  + errors.maxlength.requiredLength + ' characters allowed.';
            }
            if (errors.pattern) {
                return 'Field dowsn\'t conform to required pattern "' + this.question.pattern + '".';
            }
            if (errors.required) {
                return 'Field is empty.';
            }
            if (errors.null) {
                return 'Field is empty.';
            }
            if (errors.json) {
                return 'Syntax error in json.';
            }
            console.log(errors);
        }
        return 'Überprüfen sie bitte die Eingabe.';
    }
}
