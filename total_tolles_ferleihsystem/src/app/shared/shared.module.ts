import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { DynamicFormComponent } from './forms/dynamic-form/dynamic-form.component';
import { DynamicFormQuestionComponent } from './forms/dynamic-form/dynamic-form-question.component';

import { QuestionControlService } from './forms/question-control.service';
import { QuestionService } from './forms/question.service';
import { BaseApiService } from './rest/api-base.service';
import { ApiService } from './rest/api.service';
import { JWTService } from './rest/jwt.service';
import { LoginGuard } from './rest/guards/login.guard';
import { ModGuard } from './rest/guards/mod.guard';
import { AdminGuard } from './rest/guards/admin.guard';


import { InfoComponent } from './info/info.component';
import { InfoService } from './info/info.service';

import { myBoxComponent } from './box/box.component';
import { myDialogComponent } from './dialog/dialog.component';
import { myDropdownComponent } from './dropdown/dropdown.component';
import { myTableComponent } from './table/table.component';

import { ClickOutsideDirective } from './click-outside.directive';

@NgModule({
    imports:      [ CommonModule, FormsModule, ReactiveFormsModule ],
    declarations: [
        InfoComponent,
        myBoxComponent,
        myDialogComponent,
        myDropdownComponent,
        myTableComponent,
        DynamicFormComponent,
        DynamicFormQuestionComponent,
        ClickOutsideDirective,
    ],
    providers: [
        InfoService,
        QuestionService,
        QuestionControlService,
        ApiService,
        BaseApiService,
        JWTService,
        LoginGuard,
        ModGuard,
        AdminGuard,
    ],
    exports: [
        InfoComponent,
        myBoxComponent,
        myDialogComponent,
        myDropdownComponent,
        myTableComponent,
        DynamicFormComponent,
        DynamicFormQuestionComponent,
        ClickOutsideDirective,

        CommonModule,
        FormsModule,
        ReactiveFormsModule
    ]
})
export class SharedModule { }
