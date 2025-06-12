import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ConnectionService } from '../services/connection.service';
import { Connection } from '../models/connection.model';

@Component({
  selector: 'app-delete-connection',
  templateUrl: './delete-connection.component.html',
  styleUrls: ['./delete-connection.component.scss'],
})
export class DeleteConnectionComponent implements OnInit {
  connections: Connection[] = [];
  selectedConnection: Connection | null = null;

  constructor(
    private router: Router,
    private connectionService: ConnectionService
  ) {}

  ngOnInit(): void {
    this.loadConnections();
  }

  loadConnections(): void {
    this.connectionService.getConnections().subscribe(
      (connections) => {
        this.connections = connections;
      },
      (error) => {
        console.error('Error loading connections:', error);
      }
    );
  }

  selectConnection(connection: Connection): void {
    this.selectedConnection = connection;
  }

  deleteConnection(): void {
    if (this.selectedConnection) {
      const confirmed = confirm(
        `Are you sure you want to delete the connection: ${this.selectedConnection.name}?`
      );
      if (confirmed) {
        this.connectionService.deleteConnection(this.selectedConnection.id).subscribe({
          next: (response) => {
            // Handle success
            alert(response.message || `Connection "${this.selectedConnection?.name}" deleted successfully.`);
            this.loadConnections(); // Refresh connection list
            this.selectedConnection = null; // Reset the selected connection
          },
          error: (error) => {
            // Handle error
            console.error('Error deleting connection:', error);
            alert('Failed to delete the connection. Please try again.');
          },
        });
      }
    }
  }
  
  cancelDeletion(): void {
    this.selectedConnection = null; // Clear selection
    this.router.navigate(['/']); // Navigate back to the home page
  }  

  goToHome(): void {
    this.router.navigate(['/']);
  }
}
