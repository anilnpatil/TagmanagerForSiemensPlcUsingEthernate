import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router } from '@angular/router';
import { AuthService } from '../auth.service';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  constructor(private auth: AuthService, private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot): boolean {
    const expectedRoles: string[] = route.data['expectedRoles']; // Make sure this is plural
    const userRole = this.auth.getRole(); // Assumes your AuthService has a getRole()

    console.log('Expected roles:', expectedRoles);
    console.log('User role:', userRole);

    // Check if user's role is in the list of expected roles
    if (!expectedRoles || !expectedRoles.includes(userRole)) {
      this.router.navigate(['/unauthorized']);
      return false;
    }

    return true;
  }
}
