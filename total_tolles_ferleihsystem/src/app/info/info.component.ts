import { Component, OnInit } from '@angular/core';
import { InfoService, Message } from './info.service';
import { Observable, } from 'rxjs/Rx';
import { timeout } from 'rxjs/operator/timeout';

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
            Observable.timer(message.timeout).take(1).subscribe((() => this.remove(message)).bind(this));
        }
    }

    remove(message: Message) {
        const index = this.messages.findIndex(value => value.createdAt === message.createdAt);
        this.messages.splice(index, 1);
    }

}
