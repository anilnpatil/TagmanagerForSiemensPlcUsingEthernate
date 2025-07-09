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
import { RoleGuard } from './guards/role.guard';
import { TagValueHistoryComponent } from './tag-value-history/tag-value-history.component';
import { IntervalTagManagerComponent } from './interval-tag-manager/interval-tag-manager.component';

// const routes: Routes = [
//   { path: '', component: HomeComponent },
//   { path: 'home1', component: Home1Component, canActivate: [AuthGuard] }, // 👈 Protected
//   { path: 'add-connection', component: AddConnectionComponent, canActivate: [AuthGuard] }, // 👈 Protected },  
//   { path: 'select-connection', component: SelectConnectionComponent, canActivate: [AuthGuard] }, // 👈 Protected },
//   { path: 'delete-connection', component: DeleteConnectionComponent, canActivate: [AuthGuard] }, // 👈 Protected },
//   { path: 'tag-manager', component: TagManagerComponent, canActivate: [AuthGuard] }, // 👈 Protected },
//   { path: 'read-tags', component: ReadTagsComponent },
//   { path: 'write-tags', component: WriteTagsComponent },
//   { path: 'scheduler', component: SchedulerComponent},
//   { path: 'schedule-reading', component:ScheduleReadingComponent},
//   { path: 'auto-write-tags', component: AutoWriteTagsComponent},
//   { path: 'login', component: LoginComponent },
//   { path: 'register', component: RegisterComponent },
//   { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] }, // 👈 Protected } 
//   { path: 'user-management', component: UserManagementComponent}
// ];

const routes: Routes = [
  { path: '', component: HomeComponent },

  // Any logged-in user
  { path: 'home1', component: Home1Component, canActivate: [AuthGuard] },
  { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },

  // Admin only
  { path: 'add-connection', component: AddConnectionComponent, canActivate: [AuthGuard, RoleGuard], data: { expectedRoles: ['ADMIN'] } },
  { path: 'delete-connection', component: DeleteConnectionComponent, canActivate: [AuthGuard, RoleGuard], data: { expectedRoles: ['ADMIN'] } },
  { path: 'user-management', component: UserManagementComponent, canActivate: [AuthGuard, RoleGuard], data: { expectedRoles: ['ADMIN'] } },

  // USER or ADMIN access
  { path: 'select-connection', component: SelectConnectionComponent, canActivate: [AuthGuard, RoleGuard], data: { expectedRoles: ['USER', 'ADMIN'] } },
  { path: 'tag-manager', component: TagManagerComponent, canActivate: [AuthGuard, RoleGuard], data: { expectedRoles: ['USER', 'ADMIN'] } },
  { path: 'read-tags', component: ReadTagsComponent, canActivate: [AuthGuard, RoleGuard], data: { expectedRoles: ['USER', 'ADMIN'] } },
  { path: 'write-tags', component: WriteTagsComponent, canActivate: [AuthGuard, RoleGuard], data: { expectedRoles: ['USER', 'ADMIN'] } },
  { path: 'scheduler', component: SchedulerComponent, canActivate: [AuthGuard, RoleGuard], data: { expectedRoles: ['USER', 'ADMIN'] } },
  { path: 'schedule-reading', component: ScheduleReadingComponent, canActivate: [AuthGuard, RoleGuard], data: { expectedRoles: ['USER', 'ADMIN'] } },
  { path: 'auto-write-tags', component: AutoWriteTagsComponent, canActivate: [AuthGuard, RoleGuard], data: { expectedRoles: ['USER', 'ADMIN'] } },

  // Public
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent, canActivate: [AuthGuard, RoleGuard], data:{expectedRoles: ['ADMIN']} },
  { path: 'tag-value-history', component: TagValueHistoryComponent, canActivate: [AuthGuard, RoleGuard], data:{expectedRoles: ['USER', 'ADMIN']} },
  { path: 'interval-tag-manager', component:IntervalTagManagerComponent, canActivate: [AuthGuard, RoleGuard], data:{expectedRoles: ['USER', 'ADMIN']}},
  // Unauthorized fallback
  { path: 'unauthorized', component: HomeComponent },
];


@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
