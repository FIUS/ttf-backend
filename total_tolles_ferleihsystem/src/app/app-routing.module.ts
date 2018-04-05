import { Routes, RouterModule } from '@angular/router';
import { NgModule } from '@angular/core';

import { HomeComponent } from './home/home.component';
import { LoginComponent } from './login/login.component';

import { SearchComponent } from './search/search.component';

import { StagingComponent } from './staging/staging.component';

import { LendingComponent } from './lending/lending.component';

import { ItemsOverviewComponent } from './items/items-overview.component';
import { ItemDetailComponent } from './items/item-detail.component';

import { ItemTypesOverviewComponent } from './item-types/item-types-overview.component';
import { ItemTypeDetailComponent } from './item-types/item-type-detail.component';

import { TagsOverviewComponent } from './tags/tags-overview.component';
import { TagDetailComponent } from './tags/tag-detail.component';

import { AttributeDefinitionsOverviewComponent } from './attribute-definitions/attribute-definitions-overview.component';
import { AttributeDefinitionDetailComponent } from './attribute-definitions/attribute-definition-detail.component';

import { LoginGuard } from './shared/rest/guards/login.guard';
import { ModGuard } from './shared/rest/guards/mod.guard';
import { AdminGuard } from './shared/rest/guards/admin.guard';

const routes: Routes = [
  { path: 'search', component: SearchComponent, canActivate: [LoginGuard] },
  { path: 'staging', component: StagingComponent, canActivate: [ModGuard] },
  { path: 'lendings/:id', component: LendingComponent, canActivate: [ModGuard] },
  { path: 'items', component: ItemsOverviewComponent, canActivate: [LoginGuard] },
  { path: 'items/:id', component: ItemDetailComponent, canActivate: [LoginGuard] },
  { path: 'item-types', component: ItemTypesOverviewComponent, canActivate: [ModGuard] },
  { path: 'item-types/:id', component: ItemTypeDetailComponent, canActivate: [ModGuard] },
  { path: 'tags', component: TagsOverviewComponent, canActivate: [ModGuard] },
  { path: 'tags/:id', component: TagDetailComponent, canActivate: [ModGuard] },
  { path: 'attribute-definitions', component: AttributeDefinitionsOverviewComponent, canActivate: [ModGuard] },
  { path: 'attribute-definitions/:id', component: AttributeDefinitionDetailComponent, canActivate: [ModGuard] },
  { path: '', pathMatch: 'full', component: HomeComponent, canActivate: [LoginGuard] },
  { path: 'login', pathMatch: 'full', component: LoginComponent},
  { path: '**', redirectTo: '' }
]

@NgModule({
  imports: [
    RouterModule.forRoot(routes, {useHash: true})
  ],
  exports: [
    RouterModule
  ]
})
export class AppRoutingModule { }
