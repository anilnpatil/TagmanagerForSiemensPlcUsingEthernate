import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ConnectionService } from '../services/connection.service';
import { Connection } from '../models/connection.model';

@Component({
  selector: 'app-select-connection',
  templateUrl: './select-connection.component.html',
  styleUrls: ['./select-connection.component.scss']
})
export class SelectConnectionComponent implements OnInit {
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
    this.connectionService.getConnections().subscribe(connections => {
      this.connections = connections;
    });
  }

  selectConnection(connection: Connection): void {
    this.selectedConnection = connection;
    this.updateButtonGlow();
  }

  confirmSelection(): void {
    if (this.selectedConnection) {
      this.router.navigate(['/tag-manager'], { state: { connection: this.selectedConnection } });
    }
  }

  cancel(): void {
    if (this.selectedConnection) {
      this.selectedConnection = null; // Unselect the connection
      this.updateButtonGlow(); // Update button styles
    }
  }

  updateButtonGlow(): void {
    const okButton = document.querySelector('.header-actions button.ok');
    const cancelButton = document.querySelector('.header-actions button.cancel');
    if (this.selectedConnection) {
      okButton?.classList.add('glow-green');
      cancelButton?.classList.add('glow-yellow');
    } else {
      okButton?.classList.remove('glow-green');
      cancelButton?.classList.remove('glow-yellow');
    }
  }

  goToHome(): void {
    this.router.navigate(['/']);
  }
}
