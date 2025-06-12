// user-management.component.ts

import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

interface User {
  id: number;
  username: string;
  role: string;
}

@Component({
  selector: 'app-user-management',
  templateUrl: './user-management.component.html',
  styleUrls: ['./user-management.component.scss']
})
export class UserManagementComponent implements OnInit {
  users: User[] = [];
  filteredUsers: User[] = [];
  message: string = '';
  searchTerm: string = '';

  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit(): void {
    this.fetchUsers();
  }

  fetchUsers(): void {
    this.http.get<{ status: string; users: User[] }>('http://localhost:8081/user/all').subscribe({
      next: (res) => {
        this.users = res.users;
        this.applySearch();
      },
      error: () => {
        this.message = 'Error fetching users.';
      }
    });
  }

  applySearch(): void {
    const search = this.searchTerm.toLowerCase();
    this.filteredUsers = this.users.filter(user =>
      user.username.toLowerCase().includes(search)
    );
  }

  confirmDelete(userId: number): void {
    if (confirm('Are you sure you want to delete this user?')) {
      this.http.delete<{ status: string; message: string }>(`http://localhost:8081/user/delete/${userId}`).subscribe({
        next: (res) => {
          this.message = res.message;
          this.fetchUsers();
        },
        error: (err) => {
          this.message = err?.error?.message || 'Failed to delete user.';
        }
      });
    }
  }

  goBack(): void {
    window.history.back();
  }

  goToHome(): void {
    this.router.navigate(['/home1']);
  }
}
