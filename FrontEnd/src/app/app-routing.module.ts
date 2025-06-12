// src/app/app-routing.module.ts

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { Home1Component } from './home1/home1.component';
import { AddConnectionComponent } from './add-connection/add-connection.component';
import { SelectConnectionComponent } from './select-connection/select-connection.component';
import { DeleteConnectionComponent } from './delete-connection/delete-connection.component';
import { TagManagerComponent } from './tag-manager/tag-manager.component';
import { ReadTagsComponent } from './read-tags/read-tags.component';
import { WriteTagsComponent } from './write-tags/write-tags.component';
import { SchedulerComponent } from './scheduler/scheduler.component';
import { ScheduleReadingComponent } from './schedule-reading/schedule-reading.component';
import{ AutoWriteTagsComponent} from './auto-write-tags/auto-write-tags.component';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { AuthGuard } from './guards/auth.guard';
import { UserManagementComponent } from './user-management/user-management.component';


const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'home1', component: Home1Component, canActivate: [AuthGuard] }, // 👈 Protected
  { path: 'add-connection', component: AddConnectionComponent, canActivate: [AuthGuard] }, // 👈 Protected },  
  { path: 'select-connection', component: SelectConnectionComponent, canActivate: [AuthGuard] }, // 👈 Protected },
  { path: 'delete-connection', component: DeleteConnectionComponent, canActivate: [AuthGuard] }, // 👈 Protected },
  { path: 'tag-manager', component: TagManagerComponent, canActivate: [AuthGuard] }, // 👈 Protected },
  { path: 'read-tags', component: ReadTagsComponent },
  { path: 'write-tags', component: WriteTagsComponent },
  { path: 'scheduler', component: SchedulerComponent},
  { path: 'schedule-reading', component:ScheduleReadingComponent},
  { path: 'auto-write-tags', component: AutoWriteTagsComponent},
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] }, // 👈 Protected } 
  { path: 'user-management', component: UserManagementComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
