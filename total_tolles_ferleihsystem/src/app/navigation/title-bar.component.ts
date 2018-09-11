
import { Component, OnInit } from '@angular/core';
import { NavigationService } from './navigation-service';
import { StagingService } from './staging-service';
import { JWTService } from '../shared/rest/jwt.service';

@Component({
  selector: 'ttf-title-bar',
  templateUrl: './title-bar.component.html',
  styleUrls: ['./title-bar.component.scss']
})
export class TitleBarComponent implements OnInit {

    title: string;

    constructor(private data: NavigationService, private jwt: JWTService) { }

    ngOnInit(): void {
        this.data.currentTitle.subscribe(title => this.title = title);
    }

}
