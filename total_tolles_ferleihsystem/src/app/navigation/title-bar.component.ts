
import { Component, OnInit } from '@angular/core';
import { NavigationService } from './navigation-service';

@Component({
  selector: 'ttf-title-bar',
  templateUrl: './title-bar.component.html',
  styleUrls: ['./title-bar.component.scss']
})
export class TitleBarComponent implements OnInit {

    title: string;

    constructor(private data: NavigationService) { }

    ngOnInit(): void {
        this.data.currentTitle.subscribe(title => this.title = title);
    }

}
