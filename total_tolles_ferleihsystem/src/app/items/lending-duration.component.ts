import { Component, OnChanges, Input } from '@angular/core';

@Component({
  selector: 'ttf-lending-duration',
  templateUrl: './lending-duration.component.html'
})
export class LendingDurationComponent implements OnChanges {

    @Input() duration: number;

    minutes: number;
    hours: number;
    days: number;
    weeks: number;
    years: number;

    get valid(): boolean {
        return this.duration >= 0;
    }

    ngOnChanges() {
        let temp = Math.floor(this.duration / 60);
        this.minutes = temp % 60;
        temp = Math.floor(temp / 60);
        this.hours = temp % 24;
        temp = Math.floor(temp / 24);
        this.days = temp % 7;
        this.years = Math.floor(temp / 364);
    }

}
