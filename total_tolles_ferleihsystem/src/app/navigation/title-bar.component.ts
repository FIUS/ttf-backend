
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
    stagingEmpty: boolean;

    constructor(private data: NavigationService, private staging: StagingService, private jwt: JWTService) { }

    ngOnInit(): void {
        this.data.currentTitle.subscribe(title => this.title = title);
        this.staging.currentStaged.map(staged => staged.size === 0).subscribe(isEmpty => this.stagingEmpty = isEmpty);
    }

}
