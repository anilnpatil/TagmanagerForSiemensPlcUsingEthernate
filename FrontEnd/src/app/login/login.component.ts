import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  username = '';
  password = '';
  message = '';

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.route.queryParams.subscribe(params => {
      if (params['logout']) {
        this.message = 'Logout successful.';
      }
    });
  }

  login() {
    this.authService.login({ username: this.username, password: this.password }).subscribe({
      next: (res: any) => {
        this.authService.saveToken(res.token);
        this.router.navigate(['/home1']); // Redirect to Home1Component
      },
      error: (err) => {
        if (err.error && err.error.message) {
          this.message = err.error.message; // Display "Bad credentials"
        } else {
          this.message = 'An unexpected error occurred. Please try again.';
        }
      }
    });
  }
}