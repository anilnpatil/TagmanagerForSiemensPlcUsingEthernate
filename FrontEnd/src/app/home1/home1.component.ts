// import { Component, OnInit } from '@angular/core';
// import { Router } from '@angular/router';
// import { MatDialog } from '@angular/material/dialog';
// import { ConnectionService } from '../services/connection.service';
// import { Connection } from '../models/connection.model';

// @Component({
//   selector: 'app-home1',
//   templateUrl: './home1.component.html',
//   styleUrls: ['./home1.component.scss']
// })
// export class Home1Component implements OnInit {
//   connections: Connection[] = [];

//   constructor(
//     private router: Router,
//     private dialog: MatDialog,
//     private connectionService: ConnectionService
//   ) {}

//   ngOnInit(): void {
//     this.loadConnections();
//   }

//   loadConnections(): void {
//     this.connectionService.getConnections().subscribe(connections => {
//       this.connections = connections;
//     });
//   }

//   navigateToAddConnection(): void {
//     this.router.navigate(['/add-connection']);
//   }

//   navigateToConfigure(): void {
//     this.router.navigate(['/configure']);
//   }

//   openSelectConnection(): void {
//     this.router.navigate(['/select-connection']);
//   }

//   openDeleteConnection(): void {
//     this.router.navigate(['/delete-connection']);
//   }

//   goToHome(): void {
//     this.router.navigate(['/home']);
//   }
// }

import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { ConnectionService } from '../services/connection.service';
import { Connection } from '../models/connection.model';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-home1',
  templateUrl: './home1.component.html',
  styleUrls: ['./home1.component.scss']
})
export class Home1Component implements OnInit {
  connections: Connection[] = [];
  role: string = '';

  constructor(
    private router: Router,
    private dialog: MatDialog,
    private connectionService: ConnectionService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadConnections();
    this.role = this.authService.getRole();
  }

  loadConnections(): void {
    this.connectionService.getConnections().subscribe(connections => {
      this.connections = connections;
    });
  }

  navigateToAddConnection(): void {
    this.router.navigate(['/add-connection']);
  }

  navigateToConfigure(): void {
    this.router.navigate(['/configure']);
  }

  openSelectConnection(): void {
    this.router.navigate(['/select-connection']);
  }

  openDeleteConnection(): void {
    this.router.navigate(['/delete-connection']);
  }
  openUserRegister(): void {
    this.router.navigate(['/register']);
  }

  goToHome(): void {
    this.router.navigate(['/home']);
  }

  isAdmin(): boolean {
    return this.role === 'ADMIN';
  }

  isUser(): boolean {
    return this.role === 'USER';
  }

  logout(): void {
  this.authService.logout();
  window.location.replace('/login');
  // this.router.navigate(['/login'], { queryParams: { logout: 1 } }); 
}
}
