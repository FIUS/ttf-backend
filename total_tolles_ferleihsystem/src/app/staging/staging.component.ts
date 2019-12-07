
import {take} from 'rxjs/operators';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { FormGroup } from '@angular/forms';

import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { StagingService } from '../navigation/staging-service';
import { ApiService } from '../shared/rest/api.service';
import { QuestionService } from '../shared/forms/question.service';
import { QuestionControlService } from '../shared/forms/question-control.service';
import { QuestionBase } from '../shared/forms/question-base';
import { JWTService } from '../shared/rest/jwt.service';

@Component({
  selector: 'ttf-staging',
  templateUrl: './staging.component.html'
})
export class StagingComponent implements OnInit {

    qrScannerOpen: boolean = false;

    questions: QuestionBase<any>[] = [];
    form: FormGroup;

    constructor(private data: NavigationService, private api: ApiService,
                private staging: StagingService, private jwt: JWTService,
                private qs: QuestionService, private qcs: QuestionControlService,
                private router: Router) { }

    get valid(): boolean {
        return this.form != null && this.form.valid;
    }

    ngOnInit(): void {
        this.data.changeTitle('Total Tolles Ferleihsystem – Staging');
        this.data.changeBreadcrumbs([new Breadcrumb('Staging', '/staging')]);
        this.staging.currentStaged.subscribe(this.updateStagedItems);
        this.qs.getQuestionsFromScheme({
            allOf: [
                {
                    $ref: '#/definitions/LendingPOST',
                },
                {
                    type: 'object',
                    properties: {
                        item_ids: {
                            readOnly: true,
                            type: 'array',
                            items: {
                                type: 'integer',
                                minimum: 1
                            }
                        },
                    }
                }
            ]
        }).pipe(take(1)).subscribe(questions => {
            this.questions = questions;
            this.form = this.qcs.toFormGroup(this.questions);
            this.staging.currentStaged.pipe(take(1)).subscribe(this.updateStagedItems);
            this.form.patchValue({
                moderator: this.jwt.username(),
            });
            this.form.statusChanges.subscribe(status => {
            });
        });
    }

    newScanResult(scanResult) {
        this.staging.stage(scanResult);
    }

    updateStagedItems = staged => {
        const asList = [];
        staged.forEach(value => asList.push(value));
        if (this.form != null) {
            this.form.patchValue({
                item_ids: asList,
            });
        }
    }

    lend() {
        if (this.valid) {
            this.api.postLending(this.form.value).subscribe(data => {
                this.staging.reset();
                this.router.navigate(['lendings', data.id]);
            });
        }
    }
}
