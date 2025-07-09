import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Connection } from '../models/connection.model';
import { HttpClient } from '@angular/common/http';
import { TagMonitorService } from '../services/tag-monitor.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-scheduler',
  templateUrl: './scheduler.component.html',
  styleUrls: ['./scheduler.component.scss']
})
export class SchedulerComponent implements OnInit, OnDestroy {
  connection: Connection | null = null;
  activeInterval: number | null = null;
  private subscription!: Subscription;

  constructor(
    private router: Router,
    private http: HttpClient,
    private tagMonitorService: TagMonitorService
  ) {
    const navigation = this.router.getCurrentNavigation();
    const stateConn = navigation?.extras?.state?.['connection'];

    if (stateConn) {
      this.connection = stateConn;
      localStorage.setItem('selectedConnection', JSON.stringify(stateConn));
    } else {
      const storedConn = localStorage.getItem('selectedConnection');
      if (storedConn) {
        this.connection = JSON.parse(storedConn);
      }
    }
  }

  ngOnInit(): void {
    this.subscription = this.tagMonitorService.activeInterval$.subscribe(interval => {
      this.activeInterval = interval;
    });
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  goToScheduleReading(interval: number): void {
    if (!this.connection) return;

      localStorage.setItem('selectedConnection', JSON.stringify(this.connection));
      localStorage.setItem('selectedInterval', interval.toString());

      this.router.navigate(['/schedule-reading'], {
        state: {
          connection: this.connection,
          interval: interval
        }
    });
  }

  goToAutoWrite(): void {
    this.router.navigate(['/auto-write-tags']);
  }

  goToViewHistory(): void {
    if (this.connection) {
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

  openManageTags(interval: number): void {
    if (!this.connection) return;

    // Save to localStorage so reload works inside interval-tag-manager
    localStorage.setItem('intervalConnection', JSON.stringify(this.connection));
    localStorage.setItem('intervalValue', String(interval));

    this.router.navigate(['/interval-tag-manager'], {
      state: {
        connection: this.connection,
        interval: interval
      }
    });
  }
}
