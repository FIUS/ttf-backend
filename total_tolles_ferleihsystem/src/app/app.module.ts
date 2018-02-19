import { AppRoutingModule } from './app-routing.module';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import {HttpModule} from '@angular/http';
import { ReactiveFormsModule } from '@angular/forms';


import {SharedModule} from './shared/shared.module';

import { BreadcrumbsComponent } from './navigation/breadcrumbs.component';
import { TitleBarComponent } from './navigation/title-bar.component';
import { NavigationService } from './navigation/navigation-service';

import { HomeComponent } from './home/home.component';

import { AppComponent } from './app.component';


@NgModule({
  declarations: [
    AppComponent,

    HomeComponent,
    BreadcrumbsComponent,
    TitleBarComponent,
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
