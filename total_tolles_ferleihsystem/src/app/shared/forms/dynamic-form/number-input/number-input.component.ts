import { Component, forwardRef, Input, OnInit } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { QuestionBase } from '../../question-base';



@Component({
  selector: 'ttf-number-input',
  templateUrl: 'number-input.component.html',
  styleUrls: ['number-input.component.scss'],
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => NumberInputComponent),
    multi: true
  }]
})
export class NumberInputComponent implements ControlValueAccessor {

    @Input('value') _value: string = undefined;
    @Input() question: QuestionBase<any>;

    onChange: any = () => {};

    onTouched: any = () => {};

    get value(): number {
        if (this._value == null || this._value === '') {
            return this.question.nullValue;
        } else {
            if (this.question.valueType === 'integer') {
                return parseInt(this._value, 10);
            } else {
                return parseFloat(this._value);
            }
        }
    }

    set value(val: number) {
        if (val === this.question.nullValue) {
            this._value = undefined;
        } else {
            this._value = val.toString();
        }
        this.onChange(val);
        this.onTouched();
    }

    updateValue(event) {
        this._value = event;
        console.log(this.value);
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
