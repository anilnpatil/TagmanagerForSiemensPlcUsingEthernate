// src/app/app-routing.module.ts

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { AddConnectionComponent } from './add-connection/add-connection.component';
import { SelectConnectionComponent } from './select-connection/select-connection.component';
import { DeleteConnectionComponent } from './delete-connection/delete-connection.component';
import { TagManagerComponent } from './tag-manager/tag-manager.component';
import { ReadTagsComponent } from './read-tags/read-tags.component';
import { WriteTagsComponent } from './write-tags/write-tags.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'add-connection', component: AddConnectionComponent },  
  { path: 'select-connection', component: SelectConnectionComponent },
  { path: 'delete-connection', component: DeleteConnectionComponent },
  { path: 'tag-manager', component: TagManagerComponent },
  { path: 'read-tags', component: ReadTagsComponent },
  { path: 'write-tags', component: WriteTagsComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
