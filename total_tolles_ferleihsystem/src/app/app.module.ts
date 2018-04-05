import { AppRoutingModule } from './app-routing.module';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpModule } from '@angular/http';
import { ReactiveFormsModule } from '@angular/forms';


import { SharedModule } from './shared/shared.module';

import { BreadcrumbsComponent } from './navigation/breadcrumbs.component';
import { TitleBarComponent } from './navigation/title-bar.component';
import { NavigationService } from './navigation/navigation-service';
import { StagingService } from './navigation/staging-service';

import { HomeComponent } from './home/home.component';
import { LoginComponent } from './login/login.component';

import { StagingComponent } from './staging/staging.component';
import { StagedItemComponent } from './staging/staged-item.component';

import { ItemsOverviewComponent } from './items/items-overview.component';
import { ItemListComponent } from './items/item-list.component';
import { ItemDetailComponent } from './items/item-detail.component';
import { ItemEditComponent } from './items/item-edit.component';
import { TagsChooserComponent } from './items/tags-chooser.component';
import { AttributeEditComponent } from './items/attribute-edit.component';

import { ItemTypesOverviewComponent } from './item-types/item-types-overview.component';
import { ItemTypeListComponent } from './item-types/item-type-list.component';
import { ItemTypeDetailComponent } from './item-types/item-type-detail.component';
import { ItemTypeEditComponent } from './item-types/item-type-edit.component';

import { TagsOverviewComponent } from './tags/tags-overview.component';
import { TagListComponent } from './tags/tag-list.component';
import { TagDetailComponent } from './tags/tag-detail.component';
import { TagEditComponent } from './tags/tag-edit.component';

import { AttributeDefinitionsOverviewComponent } from './attribute-definitions/attribute-definitions-overview.component';
import { AttributeDefinitionCreateComponent } from './attribute-definitions/attribute-definition-create.component';
import { AttributeDefinitionListComponent } from './attribute-definitions/attribute-definition-list.component';
import { AttributeDefinitionDetailComponent } from './attribute-definitions/attribute-definition-detail.component';
import { AttributeDefinitionEditComponent } from './attribute-definitions/attribute-definition-edit.component';
import { LinkedAttributeDefinitionComponent } from './linked-attribute-definitions/linked-attribute-definitions.component';

import { AppComponent } from './app.component';


@NgModule({
    declarations: [
        AppComponent,
        BreadcrumbsComponent,
        TitleBarComponent,

        LoginComponent,

        HomeComponent,

        StagingComponent,
        StagedItemComponent,

        ItemsOverviewComponent,
        ItemListComponent,
        ItemDetailComponent,
        ItemEditComponent,
        TagsChooserComponent,
        AttributeEditComponent,

        ItemTypesOverviewComponent,
        ItemTypeListComponent,
        ItemTypeDetailComponent,
        ItemTypeEditComponent,

        TagsOverviewComponent,
        TagListComponent,
        TagDetailComponent,
        TagEditComponent,

        AttributeDefinitionsOverviewComponent,
        AttributeDefinitionCreateComponent,
        AttributeDefinitionListComponent,
        AttributeDefinitionDetailComponent,
        AttributeDefinitionEditComponent,
        LinkedAttributeDefinitionComponent,
    ],
    imports: [
        HttpModule,
        BrowserModule,
        ReactiveFormsModule,
        SharedModule,
        AppRoutingModule
    ],
    providers: [
        NavigationService,
        StagingService,
    ],
    bootstrap: [AppComponent]
})
export class AppModule { }
