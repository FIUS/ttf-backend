
import {timer as observableTimer,  Observable } from 'rxjs';

import {take} from 'rxjs/operators';
import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { NavigationService, Breadcrumb } from './navigation-service';


@Component({
  selector: 'ttf-breadcrumbs',
  templateUrl: './breadcrumbs.component.html',
  styleUrls: ['./breadcrumbs.component.scss']
})
export class BreadcrumbsComponent implements OnInit {

    @ViewChild('home', { static: true }) home: ElementRef;
    @ViewChild('bcContainer', { static: true }) bcContainer: ElementRef;

    hovered: boolean = false;

    breadcrumbs: Array<Breadcrumb>;

    constructor(private data: NavigationService) { }

    ngOnInit(): void {
        this.data.currentBreadcrumbs.subscribe(breadcrumbs => {
            this.breadcrumbs = breadcrumbs;
            this.scrollToBottom();
        });
    }

    breadcrumbHeight = () => {
        return this.home.nativeElement.offsetHeight;
    }

    scrollToBottom = () => {
        observableTimer(50).pipe(take(1)).subscribe(() => {
            this.bcContainer.nativeElement.scrollTop = this.bcContainer.nativeElement.scrollHeight;
        });
    }

}
