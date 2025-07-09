import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

// Angular Material Modules
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { Home1Component } from './home1/home1.component';
import { AddConnectionComponent } from './add-connection/add-connection.component';
import { SelectConnectionComponent } from './select-connection/select-connection.component';
import { TagManagerComponent } from './tag-manager/tag-manager.component';
import { ReadTagsComponent } from './read-tags/read-tags.component';
import { WriteTagsComponent } from './write-tags/write-tags.component';
import { DeleteConnectionComponent } from './delete-connection/delete-connection.component';
import { SchedulerComponent } from './scheduler/scheduler.component';
import { ScheduleReadingComponent } from './schedule-reading/schedule-reading.component';
import { AutoWriteTagsComponent } from './auto-write-tags/auto-write-tags.component';
import { RegisterComponent } from './register/register.component';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { AuthService } from './auth.service';
import { HomeComponent } from './home/home.component';
import { UserManagementComponent } from './user-management/user-management.component';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { TokenInterceptorService } from './services/token-interceptor.service';
import { TagValueHistoryComponent } from './tag-value-history/tag-value-history.component';
import { IntervalTagManagerComponent } from './interval-tag-manager/interval-tag-manager.component';

@NgModule({
  declarations: [
    AppComponent,
    Home1Component,
    AddConnectionComponent,
    SelectConnectionComponent,   
    TagManagerComponent,
    ReadTagsComponent,
    WriteTagsComponent,
    DeleteConnectionComponent,
    SchedulerComponent,
    ScheduleReadingComponent,
    AutoWriteTagsComponent,
    RegisterComponent,
    LoginComponent,
    DashboardComponent,
    HomeComponent,
    UserManagementComponent,
    TagValueHistoryComponent,
    IntervalTagManagerComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    BrowserAnimationsModule,
    
    // Angular Material Modules
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatListModule,
    MatTableModule,               // Added for mat-table
    MatProgressSpinnerModule,     // Added for mat-spinner
    MatCardModule,                // Useful for card layouts
    MatToolbarModule              // Useful for headers
  ],
  providers: [AuthService , 
    {
      provide: HTTP_INTERCEPTORS,
      useClass: TokenInterceptorService,
      multi: true
    }],
  bootstrap: [AppComponent]
})
export class AppModule { }
