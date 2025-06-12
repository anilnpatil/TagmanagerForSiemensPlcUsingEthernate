// // src/app/add-connection/add-connection.component.ts

// import { Component } from '@angular/core';
// import { Router } from '@angular/router';
// import { ConnectionService } from '../services/connection.service';
// import { Connection } from '../models/connection.model';

// @Component({
//   selector: 'app-add-connection',
//   templateUrl: './add-connection.component.html',
//   styleUrls: ['./add-connection.component.scss']
// })
// export class AddConnectionComponent {
//   connection: Connection = { id: 0, name: '', ipAddress: '', subnet: '', gateway: '' };

//   constructor(
//     private router: Router,
//     private connectionService: ConnectionService
//   ) {}

//   addConnection(): void {
//     this.connectionService.addConnection(this.connection).subscribe(() => {
//       this.clearForm();
//       this.router.navigate(['/']);
//     });
//   }

//   clearForm(): void {
//     this.connection = { id: 0, name: '', ipAddress: '', subnet: '', gateway: '' };
//   }

//   goBack(): void {
//     this.router.navigate(['/']);
//   }
// }
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ConnectionService } from '../services/connection.service';
import { Connection } from '../models/connection.model';

@Component({
  selector: 'app-add-connection',
  templateUrl: './add-connection.component.html',
  styleUrls: ['./add-connection.component.scss']
})
export class AddConnectionComponent implements OnInit {
  connection: Connection = {id: 0, name: '', ipAddress: '', subnet: '', gateway: '' };
  isFormValid: boolean = false;
  savedConnection: Connection | null = null;
  successMessage: string = '';
  errorMessage: string = '';

  constructor(private router: Router, private connectionService: ConnectionService) {}

  ngOnInit(): void {}

  validateForm(): void {
    this.isFormValid = this.connection.name !== '' && this.connection.ipAddress !== '' && this.connection.subnet !== '' && this.connection.gateway !== '';
  }

  addConnection(): void {
    if (this.isFormValid) {
      this.connectionService.addConnection(this.connection).subscribe(
        (response: Connection) => {
          this.savedConnection = response;
          this.successMessage = `Connection ${response.name} (${response.ipAddress}) saved successfully!`;
          setTimeout(() => {
            this.successMessage = '';
            this.router.navigate(['/']);
          }, 2000); // Show success message for 2 seconds before redirecting
        },
        error => {
          console.error('Error saving connection:', error);
          this.errorMessage = 'Failed to save connection, please verify  Name  and  IP Address  and try again';
          setTimeout(() => {
            this.errorMessage = '';
          }, 2000); // Show error message for 2 seconds before clearing
        }
      );
    }
  }

  clearForm(): void {
    this.connection = {id: 0, name: '', ipAddress: '', subnet: '', gateway: '' };
    this.isFormValid = false;
    this.savedConnection = null;
    this.successMessage = '';
  }

  goBack(): void {
    this.router.navigate(['/']);
  }

  goToHome(): void {
    this.router.navigate(['/']);
  }
}
