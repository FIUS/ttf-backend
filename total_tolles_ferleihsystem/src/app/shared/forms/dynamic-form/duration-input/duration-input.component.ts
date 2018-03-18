import { Component, forwardRef, Input, OnInit } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { QuestionBase } from '../../question-base';



@Component({
  selector: 'ttf-duration-input',
  templateUrl: 'duration-input.component.html',
  styleUrls: ['duration-input.component.scss'],
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => DurationInputComponent),
    multi: true
  }]
})
export class DurationInputComponent implements ControlValueAccessor {

    @Input() question: QuestionBase<any>;

    days: string;
    hours: string;
    minutes: string;
    seconds: number;

    onChange: any = () => {};

    onTouched: any = () => {};

    get value(): number {
        if ((this.days == null || this.days === '') &&
            (this.hours == null || this.hours === '') &&
            (this.minutes == null || this.minutes === '')) {
            return this.question.nullValue;
        } else {
            let val = this.seconds;
            val += parseInt(this.minutes, 10) * 60;
            val += parseInt(this.hours, 10) * 60 * 60;
            val += parseInt(this.days, 10) * 60 * 60 * 24;
            return val;
        }
    }

    @Input()
    set value(val: number) {
        if (val === this.question.nullValue) {
            this.days = undefined;
            this.hours = undefined;
            this.minutes = undefined;
        } else {
            this.seconds = val % 60;
            this.minutes = Math.floor((val / 60) % 60).toString();
            this.hours = Math.floor((val / (60 * 60)) % 24).toString();
            this.days = Math.floor(val / (60 * 60 * 24)).toString();
        }
        this.onChange(val);
        this.onTouched();
    }

    update() {
        console.log(this.value);
        this.onChange(this.value);
        this.onTouched();
    }

    updateMinutes(event) {
        this.minutes = event;
        this.update();
    }

    updateHours(event) {
        this.hours = event;
        this.update();
    }

    updateDays(event) {
        this.days = event;
        this.update();
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
