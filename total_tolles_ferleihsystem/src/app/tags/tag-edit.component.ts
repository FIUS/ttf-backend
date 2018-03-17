import { Component, OnChanges, Input } from '@angular/core';
import { Router } from '@angular/router';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';

@Component({
  selector: 'ttf-tag-edit',
  templateUrl: './tag-edit.component.html'
})
export class TagEditComponent implements OnChanges {

    private subscription: Subscription;

    @Input() tagID: number;

    tag: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    valid: boolean = false;
    data: any = {};

    constructor(private api: ApiService, private router: Router) { }

    ngOnChanges(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        this.subscription = this.api.getTag(this.tagID).subscribe(data => {
            this.tag = data;
        });
    }

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.data = data;
    }

    save(event) {
        if (this.valid) {
            this.api.putTag(this.tag.id, this.data);
        }
    }

    delete = (() => {
        this.api.deleteTag(this.tag.id).take(1).subscribe(() => this.router.navigate(['tags']));
    }).bind(this);

}
