
import {timer as observableTimer,  Observable, } from 'rxjs';

import {take} from 'rxjs/operators';
import { Component, OnInit } from '@angular/core';
import { InfoService, Message } from './info.service';


@Component({
  selector: 'ttf-info',
  templateUrl: './info.component.html'
})
export class InfoComponent implements OnInit {

    messages: Array<Message>;

    constructor(private info: InfoService) { }

    ngOnInit(): void {
        this.messages = [];
        this.info.messages.subscribe(message => this.addMessage(message));
    }

    addMessage(message: Message) {
        this.messages.push(message);
        if (message.timeout != null && message.timeout > 0) {
            observableTimer(message.timeout).pipe(take(1)).subscribe((() => this.remove(message)).bind(this));
        }
    }

    remove(message: Message) {
        const index = this.messages.findIndex(value => value.createdAt === message.createdAt);
        this.messages.splice(index, 1);
    }

}
