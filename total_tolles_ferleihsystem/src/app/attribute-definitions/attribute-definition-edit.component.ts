import { Component, OnChanges, Input, ViewChild, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';
import { DynamicFormComponent } from '../shared/forms/dynamic-form/dynamic-form.component';
import { JWTService } from '../shared/rest/jwt.service';
import { QuestionBase } from 'app/shared/forms/question-base';
import { FormGroup } from '@angular/forms';
import { QuestionService } from 'app/shared/forms/question.service';
import { QuestionControlService } from 'app/shared/forms/question-control.service';

@Component({
  selector: 'ttf-attribute-definition-edit',
  templateUrl: './attribute-definition-edit.component.html'
})
export class AttributeDefinitionEditComponent implements OnChanges, OnDestroy {

    private subscription: Subscription;

    @ViewChild(DynamicFormComponent) form;

    @Input() attributeDefinitionID: number;

    questions: QuestionBase<any>[] = [];
    testForm: FormGroup;

    attrDef: any = null;

    currentAttrDef: any;

    constructor(private api: ApiService, private router: Router, private jwt: JWTService,
        private qs: QuestionService, private qcs: QuestionControlService) { }

    ngOnChanges(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        this.subscription = this.api.getAttributeDefinition(this.attributeDefinitionID).subscribe(data => {
            this.attrDef = data;
            this.updateTestForm();
        });
    }

    ngOnDestroy(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
    }

    updateTestForm() {
        let attribute_definition = this.attrDef;
        if (this.currentAttrDef != null && this.currentAttrDef.name != null && this.currentAttrDef.name !== '') {
            attribute_definition = this.currentAttrDef;
        }
        let schema: any = {};
        if (attribute_definition.jsonschema != null && attribute_definition.jsonschema !== '') {
            schema = JSON.parse(attribute_definition.jsonschema);
        }
        schema.type = attribute_definition.type;
        if (attribute_definition.type === 'string') {
            const maxLength = (window as any).maxDBStringLength - 2;
            if (schema.maxLength == null || schema.maxLength > maxLength) {
                schema.maxLength = maxLength;
            }
        }
        this.qs.getQuestionsFromScheme({
            type: 'object',
            properties: {
                [attribute_definition.name]: schema,
            }
        }).take(1).subscribe(questions => {
            this.questions = questions;
            this.questions.forEach(qstn => {
                if (qstn.key === attribute_definition.name) {
                    qstn.autocompleteData = this.api.getAttributeAutocomplete(this.attrDef);
                }
            });
            this.testForm = this.qcs.toFormGroup(this.questions);
        });
    }

    questionTrackFn(index: any, question: any) {
        return question.key;
    }

    save = (event) => {
        if (event.jsonschema !== '') {
            // Try formatting the jsonscheme before saving to help editing later
            try {
                event.jsonschema = JSON.stringify(JSON.parse(event.jsonschema), undefined, '\t');
            } catch (error) {}
        }
        this.api.putAttributeDefinition(this.attrDef.id, event).take(1).subscribe(() => {
            this.form.saveFinished(true);
            this.updateTestForm();
        }, () => {
            this.form.saveFinished(false);
        });
    }

    delete = () => {
        this.api.deleteAttributeDefinition(this.attrDef.id).take(1).subscribe(() => this.router.navigate(['attribute-definitions']));
    };

}
