import { Component, forwardRef, Input, OnInit } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { QuestionBase } from '../../question-base';



@Component({
  selector: 'ttf-dropdown-input',
  templateUrl: 'dropdown-input.component.html',
  styleUrls: ['dropdown-input.component.scss'],
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => DropdownInputComponent),
    multi: true
  }]
})
export class DropdownInputComponent implements ControlValueAccessor {

    @Input() question: QuestionBase<any>;

    searchString: string = '';

    chosenOption: string = '';

    onChange: any = () => {};

    onTouched: any = () => {};

    get value(): string {
        if (this.chosenOption == null || this.chosenOption === '') {
            return this.question.nullValue;
        } else {
            return this.chosenOption;
        }
    }

    @Input()
    set value(val: string) {
        if (val === this.question.nullValue) {
            this.chosenOption = '';
        } else {
            this.chosenOption = val;
            this.searchString = val;
        }
        this.onChange(val);
        this.onTouched();
    }

    updateValue(searchString) {
        if (this.question != null && this.question.options != null) {
            this.question.options.forEach(option => {
                if (option === searchString) {
                    this.chosenOption = option;
                    this.update();
                    return;
                }
            });
        }
    }

    update() {
        this.onChange(this.value);
        this.onTouched();
    }

    registerOnChange(fn) {
        this.onChange = fn;
    }

    registerOnTouched(fn) {
        this.onTouched = fn;
    }

    writeValue(value) {
        if (value) {
            this.value = value;
        }
    }
}
