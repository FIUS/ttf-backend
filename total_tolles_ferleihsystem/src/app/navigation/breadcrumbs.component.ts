import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { NavigationService, Breadcrumb } from './navigation-service';
import { Observable } from 'rxjs/Rx';


@Component({
  selector: 'ttf-breadcrumbs',
  templateUrl: './breadcrumbs.component.html',
  styleUrls: ['./breadcrumbs.component.scss']
})
export class BreadcrumbsComponent implements OnInit {

    @ViewChild('home') home: ElementRef;
    @ViewChild('bcContainer') bcContainer: ElementRef;

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
        Observable.timer(50).take(1).subscribe(() => {
            this.bcContainer.nativeElement.scrollTop = this.bcContainer.nativeElement.scrollHeight;
        });
    }

}
