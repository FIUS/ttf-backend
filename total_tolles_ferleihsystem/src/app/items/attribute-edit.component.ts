import { Component, OnChanges, Input, OnDestroy, SimpleChanges } from '@angular/core';
import { Router } from '@angular/router';
import { FormGroup } from '@angular/forms';
import { Subscription, Observable } from 'rxjs/Rx';

import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { QuestionService } from '../shared/forms/question.service';
import { QuestionControlService } from '../shared/forms/question-control.service';
import { QuestionBase } from '../shared/forms/question-base';

@Component({
  selector: 'ttf-attribute-edit',
  templateUrl: './attribute-edit.component.html'
})
export class AttributeEditComponent implements OnChanges, OnDestroy {

    private itemSubscription: Subscription;
    private attributeSubscription: Subscription;
    private formStatusChangeSubscription: Subscription;

    @Input() itemID: number;
    @Input() attributeID: number;

    item: ApiObject;
    attribute: ApiObject;

    questions: QuestionBase<any>[] = [];
    form: FormGroup;

    saved: boolean = true;

    constructor(private api: ApiService, private router: Router,
                private qs: QuestionService, private qcs: QuestionControlService) { }

    ngOnChanges(changes: SimpleChanges): void {
        if (this.itemSubscription != null) {
            this.itemSubscription.unsubscribe();
        }
        if (this.itemID != null) {
            this.itemSubscription = this.api.getItem(this.itemID).subscribe(data => {
                this.item = data;
                if (this.item != null) {
                    if (this.attributeSubscription != null) {
                        this.attributeSubscription.unsubscribe();
                    }
                    if (this.attributeID != null) {
                        this.attributeSubscription = this.api.getAttribute(this.item, this.attributeID).subscribe(data => {
                            this.attribute = data;
                            if (this.form == null) {
                                this.getQuestion(this.attribute);
                            }
                            this.saved = true;
                        });
                    }
                }
            });
        }
    }

    getQuestion(attribute) {
        let schema: any = {};
        if (attribute.attribute_definition.jsonschema != null && attribute.attribute_definition.jsonschema !== '') {
            schema = JSON.parse(attribute.attribute_definition.jsonschema);
        }
        schema.type = attribute.attribute_definition.type;
        if (attribute.attribute_definition.type === 'string') {
            const maxLength = (window as any).maxDBStringLength - 2;
            if (schema.maxLength == null || schema.maxLength > maxLength) {
                schema.maxLength = maxLength;
            }
        }
        this.qs.getQuestionsFromScheme({
            type: 'object',
            properties: {
                [attribute.attribute_definition.name]: schema,
            }
        }).take(1).subscribe(questions => {
            this.questions = questions;
            this.questions.forEach(qstn => {
                if (qstn.key === attribute.attribute_definition.name) {
                    qstn.autocompleteData = this.api.getAttributeAutocomplete(attribute.attribute_definition);
                }
            });
            this.form = this.qcs.toFormGroup(this.questions);
            let value = attribute.value;
            try {
                value = JSON.parse(value);
            } catch (SyntaxError) {}
            this.form.patchValue({
                [attribute.attribute_definition.name]: value,
            });
            if (this.formStatusChangeSubscription != null) {
                this.formStatusChangeSubscription.unsubscribe();
            }
            this.formStatusChangeSubscription = this.form.statusChanges.filter(status => status === 'VALID').map(status => {
                this.saved = false;
                return JSON.stringify(this.form.value[attribute.attribute_definition.name]);
            }).debounceTime(700).subscribe(value => {
                this.api.putAttribute(this.item, this.attributeID, value);
            })
        });
    }

    questionTrackFn(index: any, question: any) {
        return question.key;
    }

    ngOnDestroy(): void {
        if (this.itemSubscription != null) {
            this.itemSubscription.unsubscribe();
        }
        if (this.attributeSubscription != null) {
            this.attributeSubscription.unsubscribe();
        }
        if (this.formStatusChangeSubscription != null) {
            this.formStatusChangeSubscription.unsubscribe();
        }
    }

}
