import { AppRoutingModule } from './app-routing.module';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpModule } from '@angular/http';
import { ReactiveFormsModule } from '@angular/forms';


import { SharedModule } from './shared/shared.module';

import { BreadcrumbsComponent } from './navigation/breadcrumbs.component';
import { TitleBarComponent } from './navigation/title-bar.component';
import { NavigationService } from './navigation/navigation-service';

import { HomeComponent } from './home/home.component';
import { LoginComponent } from './login/login.component';

import { ItemTypesOverviewComponent } from './item-types/item-types-overview.component';
import { ItemTypeListComponent } from './item-types/item-type-list.component';

import { AppComponent } from './app.component';


@NgModule({
    declarations: [
        AppComponent,
        BreadcrumbsComponent,
        TitleBarComponent,

        LoginComponent,

        HomeComponent,
        ItemTypesOverviewComponent,
        ItemTypeListComponent,
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
    ],
    bootstrap: [AppComponent]
})
export class AppModule { }
