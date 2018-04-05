import { Component, OnInit, OnDestroy, Input, Output, EventEmitter } from '@angular/core';
import { Subscription } from 'rxjs/Rx';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';

@Component({
  selector: 'ttf-item-lending',
  templateUrl: './item-lending.component.html'
})
export class ItemLendingComponent implements OnInit, OnDestroy {


    @Input() itemLending: any;
    @Output() return: EventEmitter<number> = new EventEmitter<number>();

    open: boolean = false;


    constructor(private api: ApiService) { }

    ngOnInit(): void {
    }

    ngOnDestroy(): void {
    }
}
