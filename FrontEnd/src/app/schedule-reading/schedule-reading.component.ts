import { Component, OnInit, OnDestroy } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { TagMonitorService } from '../services/tag-monitor.service';
import { Subscription } from 'rxjs';
import { Connection } from '../models/connection.model';

@Component({
  selector: 'app-schedule-reading',
  templateUrl: './schedule-reading.component.html',
  styleUrls: ['./schedule-reading.component.scss']
})
export class ScheduleReadingComponent implements OnInit, OnDestroy {
  // Component state
  connection: Connection | null = null;
  interval: number = 0;
  savedTags: string[] = [];
  tagValues: { tag: string; value: any; timestamp?: Date }[] = [];
  saveStatus: 'idle' | 'saving' | 'success' | 'error' = 'idle';
  errorMessage: string | null = null;
  lastUpdated: Date | null = null;
  loading = false;

  // Subscriptions
  private subscriptions: Subscription[] = [];
  private errorSubscription?: Subscription;

  constructor(
    private http: HttpClient,
    private router: Router,
    private tagMonitorService: TagMonitorService
  ) {}

  ngOnInit(): void {
    this.initializeComponent();
    this.setupSubscriptions();
  }

  private initializeComponent(): void {
    const state = history.state;
    this.connection = state['connection'];
    this.interval = state['interval'] ?? 0;

    if (!this.connection) {
      this.router.navigate(['/']);
      return;
    }

    this.resetComponentState();
    this.initializeMonitoring();
  }

  private resetComponentState(): void {
    this.errorMessage = null;
    this.loading = true;
    this.tagValues = [];
  }

  private initializeMonitoring(): void {
    if (this.shouldUseExistingMonitoring()) {
      this.loading = false;
    } else {
      this.fetchSavedTags();
    }
  }

  private shouldUseExistingMonitoring(): boolean {
    return this.tagMonitorService.isActive() && 
           this.tagMonitorService.currentInterval === this.interval;
  }

  private setupSubscriptions(): void {
    this.setupErrorSubscription();
    this.setupDataSubscriptions();
  }

  private setupErrorSubscription(): void {
    this.errorSubscription = this.tagMonitorService.errorMessage$.subscribe({
      next: (msg) => {
        this.handleErrorMessage(msg);
      },
      error: (err) => {
        console.error('Error subscription error:', err);
      }
    });
  }

  private handleErrorMessage(msg: string | null): void {
    this.errorMessage = msg;
    if (msg) {
      this.loading = false;
      this.tagValues = [];
    }
  }

  private setupDataSubscriptions(): void {
    this.subscriptions.push(
      this.tagMonitorService.tagValues$.subscribe(values => {
        this.handleTagValues(values);
      }),
      this.tagMonitorService.saveStatus$.subscribe(status => {
        this.saveStatus = status;
      }),
      this.tagMonitorService.lastUpdated$.subscribe(time => {
        this.lastUpdated = time;
      })
    );
  }

  private handleTagValues(values: { tag: string; value: any; timestamp?: Date }[]): void {
    this.tagValues = values;
    this.loading = false;
    if (values?.length > 0) {
      this.errorMessage = null;
    }
  }

  fetchSavedTags(): void {
    this.loading = true;
    this.errorMessage = null;

    this.http.get<string[]>(
      `http://localhost:8081/getSavedTagsById?connectionId=${this.connection!.id}`
    ).subscribe({
      next: (tags) => this.handleTagsResponse(tags),
      error: (err) => this.handleTagsError(err)
    });
  }

  private handleTagsResponse(tags: string[]): void {
    if (tags.length > 0) {
      this.savedTags = tags;
      this.startTagMonitoring();
    } else {
      this.handleNoTagsConfigured();
    }
  }

  private startTagMonitoring(): void {
    this.tagMonitorService.startMonitoring(
      this.connection!.ipAddress,
      this.interval,
      this.savedTags,
      this.connection!.id
    );
  }

  private handleNoTagsConfigured(): void {
    this.loading = false;
    this.tagValues = [];
    this.errorMessage = 'No tags configured for monitoring';
  }

  private handleTagsError(err: any): void {
    this.loading = false;
    this.errorMessage = err.error?.message || 'Failed to load saved tags';
    this.tagValues = [];
  }

  clearError(): void {
    this.errorMessage = null;
    this.tagMonitorService.clearErrorMessage();
  }

  goBack(): void {
    this.navigateToScheduler();
  }

  goHome(): void {
    this.navigateToScheduler();
  }

  private navigateToScheduler(): void {
    this.router.navigate(['/scheduler'], {
      state: { connection: this.connection }
    });
  }

  stopBackground(): void {
    this.tagMonitorService.stopMonitoring();
    this.navigateToScheduler();
  }

  ngOnDestroy(): void {
    this.cleanupSubscriptions();
  }

  private cleanupSubscriptions(): void {
    this.errorSubscription?.unsubscribe();
    this.subscriptions.forEach(sub => sub.unsubscribe());
    this.subscriptions = [];
  }
}