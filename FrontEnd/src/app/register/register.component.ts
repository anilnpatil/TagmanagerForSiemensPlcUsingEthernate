import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';
import { ApiResponse } from '../models/api-response.model';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
  username = '';
  password = '';
  role = 'USER';
  message = '';
  success = false;

  constructor(private auth: AuthService, private router: Router) {}

  isFormValid(): boolean {
    return this.username.trim() !== '' && this.password.trim() !== '' && this.role !== '';
  }

  register(): void {
    this.message = '';
    this.auth.register({
      username: this.username,
      password: this.password,
      role: this.role
    }).subscribe({
      next: (res: ApiResponse) => {
        if (res.status === 'success') {
          this.success = true;
          this.message = res.message;
          setTimeout(() => this.message = '' , 1500); //this.router.navigate(['/register']), 2000);
        } else {
          this.success = false;
          this.message = res.message;
        }
      },
      error: (err) => {
        const fullMsg = err?.error?.message || '';
        this.success = false;
        if (fullMsg.includes('Duplicate entry')) {
          this.message = 'Username already exists.';
        } else {
          this.message = fullMsg || 'Registration failed.';
        }
      }
    });
  }

  goToHome(): void {
    this.router.navigate(['/home1']);
  }
}


