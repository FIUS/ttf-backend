
import {take} from 'rxjs/operators';
import { Component, OnChanges, Input, OnDestroy, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs';
import { DynamicFormComponent } from '../shared/forms/dynamic-form/dynamic-form.component';
import { JWTService } from '../shared/rest/jwt.service';

@Component({
  selector: 'ttf-tag-edit',
  templateUrl: './tag-edit.component.html'
})
export class TagEditComponent implements OnChanges, OnDestroy {

    private subscription: Subscription;

    @ViewChild(DynamicFormComponent, { static: true }) form;

    @Input() tagID: number;

    tag: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    constructor(private api: ApiService, private router: Router, private jwt: JWTService) { }

    ngOnChanges(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        this.subscription = this.api.getTag(this.tagID).subscribe(data => {
            this.tag = data;
        });
    }

    ngOnDestroy(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
    }

    save = (event) => {
        this.api.putTag(this.tag.id, event).pipe(take(1)).subscribe(() => {
            this.form.saveFinished(true);
        }, () => {
            this.form.saveFinished(false);
        });
    }

    delete = () => {
        this.api.deleteTag(this.tag.id).pipe(take(1)).subscribe(() => this.router.navigate(['tags']));
    };

}
