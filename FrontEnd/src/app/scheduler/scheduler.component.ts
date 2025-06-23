import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { Connection } from '../models/connection.model';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-scheduler',
  templateUrl: './scheduler.component.html',
  styleUrls: ['./scheduler.component.scss']
})
export class SchedulerComponent {
  connection: Connection | null = null;

  constructor(
    private router: Router,
    private http: HttpClient
  ) {
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras.state) {
      this.connection = navigation.extras.state['connection'];
    }
  }

  goToScheduleReading(interval: number): void {
    const storedConnection = localStorage.getItem('selectedConnection');
    if (storedConnection) {
      this.connection = JSON.parse(storedConnection);
      this.router.navigate(['/schedule-reading'], {
        state: {
          connection: this.connection,
          interval: interval
        }
      });
     }//else{
    //    const storedConnection = localStorage.getItem('selectedConnection');
    //     if (storedConnection) {
    //       this.connection = JSON.parse(storedConnection);
    //       if (this.connection) {
    //         this.router.navigate(['/schedule-reading'], {
    //           state:{
    //             connection: this.connection
    //             interval: interval
    //                         }
    //         });
    //       }
    //     } else {
    //       this.router.navigate(['/tag-manager']);
    //     }
    // }
  }

  goToAutoWrite(): void {
    // Implementation for Auto Write would go here
    this.router.navigate(['/auto-write-tags']);
  }

  goToViewHistory(): void {
  const storedConnection = localStorage.getItem('selectedConnection');
  if (storedConnection) {
    this.connection = JSON.parse(storedConnection);
    this.router.navigate(['/tag-value-history'], {
      state: {
        connection: this.connection
      }
    });
  }
}


  goBack(): void {
    this.router.navigate(['/tag-manager']);
  }
}