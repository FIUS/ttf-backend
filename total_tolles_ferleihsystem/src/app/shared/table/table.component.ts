import { Component, Input, Output, EventEmitter } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

export class TableRow {

    id: number;
    route?: (string | number)[];
    routeRelative?: boolean;
    content: string[];

    constructor(id: number, content: string[], route?: (string | number)[], routeRelative?: boolean) {
        this.id = id;
        this.content = content;
        this.route = route;
        this.routeRelative = routeRelative;
    }
}

@Component({
    selector: 'ttf-table',
    templateUrl: './table.component.html',
    styleUrls: ['./table.component.scss']
})
export class myTableComponent {

    @Input() selected: number;
    @Input() headings: string[];
    @Input() rows: TableRow[];

    @Output() selectedChange = new EventEmitter();

    constructor(private router: Router, private route: ActivatedRoute){}

    selectRow(row: TableRow) {
        if (row.route != undefined) {
            if (row.routeRelative) {
                this.router.navigate(row.route, {relativeTo: this.route});
            } else {
                this.router.navigate(row.route);
            }
        } else {
            this.selectedChange.emit(row.id);
        }
    }
}
