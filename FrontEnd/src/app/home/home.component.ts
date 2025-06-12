import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { ConnectionService } from '../services/connection.service';
import { Connection } from '../models/connection.model';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  connections: Connection[] = [];

  constructor(
    private router: Router,
    private dialog: MatDialog,
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

  goToHome(): void {
    this.router.navigate(['/home']);
  }
}
