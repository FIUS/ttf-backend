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

    days: string = '0';
    time: string = '00:00';
    seconds: number = 0;

    onChange: any = () => {};

    onTouched: any = () => {};

    get value(): number {
        if ((this.days == null || this.days === '') &&
            (this.time == null || this.time === '')) {
            return this.question.nullValue;
        } else {
            let val = this.seconds;
            const temp = this.time.split(':');
            const minutes = temp[1];
            const hours = temp[0];
            if (minutes != null && minutes !== '') {
                val += parseInt(minutes, 10) * 60;
            }
            if (hours != null && hours !== '') {
                val += parseInt(hours, 10) * 60 * 60;
            }
            if (this.days != null && this.days !== '') {
                val += parseInt(this.days, 10) * 60 * 60 * 24;
            }
            return val;
        }
    }

    @Input()
    set value(val: number) {
        if (val === this.question.nullValue) {
            this.days = '0';
            this.time = '00:00';
            this.seconds = 0;
        } else {
            this.seconds = val % 60;
            const minutes = Math.floor((val / 60) % 60).toString();
            const hours = Math.floor((val / (60 * 60)) % 24).toString();
            this.time = ((hours.length < 2 ? '0' + hours : hours) + ':' +
                         (minutes.length < 2 ? '0' + minutes : minutes));
            this.days = Math.floor(val / (60 * 60 * 24)).toString();
        }
        this.onChange(val);
        this.onTouched();
    }

    update() {
        this.onChange(this.value);
        this.onTouched();
    }

    updateTime(event) {
        if (event == null || event === '') {
            this.time = '00:00';
            return;
        }
        this.time = event;
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
