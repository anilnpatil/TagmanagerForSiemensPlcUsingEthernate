import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class TagMonitorService {
  private eventSource: EventSource | null = null;
  private connectionId: number = 0;

  // Subjects and Observables
  private tagValuesSubject = new BehaviorSubject<{ tag: string, value: any, timestamp?: Date }[]>([]);
  tagValues$: Observable<{ tag: string, value: any, timestamp?: Date }[]> = this.tagValuesSubject.asObservable();

  private saveStatusSubject = new BehaviorSubject<'idle' | 'saving' | 'success' | 'error'>('idle');
  saveStatus$: Observable<'idle' | 'saving' | 'success' | 'error'> = this.saveStatusSubject.asObservable();

  private lastUpdatedSubject = new BehaviorSubject<Date | null>(null);
  lastUpdated$: Observable<Date | null> = this.lastUpdatedSubject.asObservable();

  private errorMessageSubject = new BehaviorSubject<string | null>(null);
  errorMessage$: Observable<string | null> = this.errorMessageSubject.asObservable();

  private activeIntervalSubject = new BehaviorSubject<number | null>(null);
  activeInterval$: Observable<number | null> = this.activeIntervalSubject.asObservable();

  private isMonitoringSubject = new BehaviorSubject<boolean>(false);
  isMonitoring$: Observable<boolean> = this.isMonitoringSubject.asObservable();

  constructor(private http: HttpClient) {}

  startMonitoring(ip: string, interval: number, tags: string[], connectionId: number): void {
    this.stopMonitoring();
    
    this.connectionId = connectionId;
    this.activeIntervalSubject.next(interval);
    this.isMonitoringSubject.next(true);
    
    const tagsParam = encodeURIComponent(tags.join(','));
    const url = `http://localhost:8083/getTagValuesByInterval?ip=${ip}&interval=${interval}&tags=${tagsParam}`;
    
    this.eventSource = new EventSource(url);

    this.eventSource.addEventListener('message', (event) => {
      try {
        const dataStr = event.data.startsWith('data: ') ? event.data.substring(6) : event.data;
        
        // Check for error response first
        if (this.isErrorResponse(dataStr)) {
          this.handleErrorResponse(dataStr);
          return;
        }

        const response = JSON.parse(dataStr);
        
        if (response.error) {
          this.handleGenericError(response.message);
          return;
        }

        this.handleSuccessfulResponse(response);
      } catch (err) {
        this.handleParseError(err);
      }
    });

    this.eventSource.addEventListener('error', () => {
      if (!this.eventSource) return;
      this.handleConnectionError();
    });
  }

  private isErrorResponse(dataStr: string): boolean {
    try {
      const data = JSON.parse(dataStr);
      return data && data.message && data.details;
    } catch {
      return false;
    }
  }

  private handleErrorResponse(dataStr: string): void {
    const errorData = JSON.parse(dataStr);
    const errorMessage = `${errorData.message}: ${errorData.details}`;
    this.errorMessageSubject.next(errorMessage);
    this.tagValuesSubject.next([]);
    this.isMonitoringSubject.next(false);
  }

  private handleGenericError(message?: string): void {
    this.errorMessageSubject.next(message || 'Server error');
    this.stopMonitoring();
  }

  private handleSuccessfulResponse(response: any): void {
    const tagValues = Object.entries(response.data).map(([tag, value]) => ({
      tag,
      value: value !== null ? value : 'N/A',
      timestamp: new Date(response.timestamp)
    }));

    this.tagValuesSubject.next(tagValues);
    this.lastUpdatedSubject.next(new Date());
    this.errorMessageSubject.next(null);

    this.saveDataToDatabase({
      connectionId: this.connectionId,
      timestamp: response.timestamp,
      tagValues: this.convertTagArrayToMap(tagValues)
    });
  }

  private handleParseError(err: any): void {
    console.error('Parse error in SSE:', err);
    this.errorMessageSubject.next('Error processing data from server');
    this.stopMonitoring();
  }

  private handleConnectionError(): void {
    if (!this.errorMessageSubject.value) {
      this.errorMessageSubject.next('Connection to server failed. Please check your network and server status.');
    }
    this.isMonitoringSubject.next(false);
  }

  stopMonitoring(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }

    this.isMonitoringSubject.next(false);
    this.activeIntervalSubject.next(null);
    this.tagValuesSubject.next([]);
    this.lastUpdatedSubject.next(null);
    this.saveStatusSubject.next('idle');
    // Don't clear error message here - let component handle it
  }

  clearErrorMessage(): void {
    this.errorMessageSubject.next(null);
  }

  isMonitoringInterval(interval: number): boolean {
    return this.isActive() && this.activeIntervalSubject.value === interval;
  }

  get currentInterval(): number | null {
    return this.activeIntervalSubject.value;
  }

  isActive(): boolean {
    return this.eventSource !== null;
  }

  private saveDataToDatabase(data: any): void {
    this.saveStatusSubject.next('saving');

    this.http.post<{ status: string, message: string }>('http://localhost:8081/tagValues/save', data)
      .subscribe({
        next: () => {
          this.saveStatusSubject.next('success');
          setTimeout(() => this.saveStatusSubject.next('idle'), 3000);
        },
        error: (err) => {
          console.error('Error saving data:', err);
          const message = err.error?.message || err.error?.error || err.message || 'Failed to save data!';
          this.errorMessageSubject.next(message);
          this.saveStatusSubject.next('error');
          setTimeout(() => this.saveStatusSubject.next('idle'), 3000);
        }
      });
  }

  private convertTagArrayToMap(tagArray: { tag: string; value: any }[]): { [key: string]: any } {
    return tagArray.reduce((acc, {tag, value}) => {
      acc[tag] = value;
      return acc;
    }, {} as { [key: string]: any });
  }
}