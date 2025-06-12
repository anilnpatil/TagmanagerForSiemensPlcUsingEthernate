// src/app/app.module.ts

import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { AddConnectionComponent } from './add-connection/add-connection.component';
import { SelectConnectionComponent } from './select-connection/select-connection.component';
import { TagManagerComponent } from './tag-manager/tag-manager.component';
import { ReadTagsComponent } from './read-tags/read-tags.component';
import { WriteTagsComponent } from './write-tags/write-tags.component';
import { DeleteConnectionComponent } from './delete-connection/delete-connection.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    AddConnectionComponent,
    SelectConnectionComponent,   
    TagManagerComponent,
    ReadTagsComponent,
    WriteTagsComponent,
    DeleteConnectionComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    BrowserAnimationsModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatListModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
