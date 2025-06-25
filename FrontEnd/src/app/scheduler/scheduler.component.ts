import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Connection } from '../models/connection.model';
import { TagMonitorService } from '../services/tag-monitor.service';
import { Subscription } from 'rxjs';
import { HttpClient } from '@angular/common/http';

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
    if (navigation?.extras.state) {
      this.connection = navigation.extras.state['connection'];
    } else {
      const storedConnection = localStorage.getItem('selectedConnection');
      if (storedConnection) {
        this.connection = JSON.parse(storedConnection);
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

    // If clicking the already active interval, just navigate to the page
    if (this.activeInterval === interval) {
      this.router.navigate(['/schedule-reading'], {
        state: {
          connection: this.connection,
          interval: interval
        }
      });
      return;
    }

    // If another interval is active, prevent navigation
    if (this.activeInterval !== null && this.activeInterval !== interval) {
      return;
    }

    // For new interval, proceed with navigation
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

  stopBackground(): void {
    this.tagMonitorService.stopMonitoring();
    this.activeInterval = null;
  }
}