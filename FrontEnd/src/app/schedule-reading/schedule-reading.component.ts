// import { Component, OnInit, OnDestroy } from '@angular/core';
// import { HttpClient } from '@angular/common/http';
// import { Router } from '@angular/router';
// import { Connection } from '../models/connection.model';

// @Component({
//   selector: 'app-schedule-reading',
//   templateUrl: './schedule-reading.component.html',
//   styleUrls: ['./schedule-reading.component.scss']
// })
// export class ScheduleReadingComponent implements OnInit, OnDestroy {
//   connection: Connection | null = null;
//   interval: number = 0;
//   tagValues: { tag: string; value: any; timestamp?: Date }[] = [];
//   loading = true;
//   errorMessage: string | null = null;
//   lastUpdated: Date | null = null;

//   private eventSource: EventSource | null = null;
//   private savedTags: string[] = [];

//   constructor(private http: HttpClient, private router: Router) {}

//   ngOnInit(): void {
//     const state = history.state;
//     this.connection = state['connection'];
//     this.interval = state['interval'] ?? 0;

//     if (this.connection) {
//       this.fetchSavedTags();
//     } else {
//       this.router.navigate(['/']);
//     }
//   }

//   ngOnDestroy(): void {
//     this.closeEventSource();
//   }

//   private closeEventSource(): void {
//     if (this.eventSource) {
//       this.eventSource.close();
//       this.eventSource = null;
//     }
//   }

//   fetchSavedTags(): void {
//     if (!this.connection) return;

//     const connectionId = this.connection.id;
//     this.http.get<string[]>(`http://localhost:8081/getSavedTagsById?connectionId=${connectionId}`)
//       .subscribe({
//         next: (tags) => {
//           if (tags.length > 0) {
//             this.savedTags = tags;
//             this.startSSEConnection(tags);
//           } else {
//             this.loading = false;
//             this.tagValues = [];
//           }
//         },
//         error: () => {
//           this.loading = false;
//           this.errorMessage = 'Failed to load saved tags.';
//         }
//       });
//   }

//   private startSSEConnection(tags: string[]): void {
//     if (!this.connection) return;

//     this.closeEventSource();
    
//     const tagsParam = encodeURIComponent(tags.join(','));
//     const url = `http://localhost:8083/getTagValuesByInterval?ip=${this.connection.ipAddress}&interval=${this.interval}&tags=${tagsParam}`;

//     this.loading = true;
//     this.errorMessage = null;

//     this.eventSource = new EventSource(url);

//     this.eventSource.addEventListener('message', (event) => {
//       try {
//         // Remove the "data: " prefix if present
//         const dataStr = event.data.startsWith('data: ') ? event.data.substring(6) : event.data;
//         const response = JSON.parse(dataStr);

//         if (response.error) {
//           this.handleError(response.message || 'Server error');
//           return;
//         }

//         this.tagValues = Object.entries(response.data).map(([tag, value]) => ({
//           tag,
//           value: value !== null ? value : 'N/A',
//           timestamp: new Date(response.timestamp)
//         }));
        
//         this.lastUpdated = new Date();
//         this.loading = false;
//       } catch (e) {
//         console.error('Error parsing SSE data:', e);
//         this.handleError('Error processing data from server');
//       }
//     });

//     this.eventSource.addEventListener('error', () => {
//       if (!this.errorMessage) {
//         this.handleError('Connection to server failed');
//       }
//       this.closeEventSource();
//     });
//   }

//   private handleError(message: string): void {
//     this.errorMessage = message;
//     this.loading = false;
//     this.closeEventSource();
//   }

//   goBack(): void {
//     this.router.navigate(['/tag-manager']);
//   }
// }

import { Component, OnInit, OnDestroy } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Connection } from '../models/connection.model';

@Component({
  selector: 'app-schedule-reading',
  templateUrl: './schedule-reading.component.html',
  styleUrls: ['./schedule-reading.component.scss']
})
export class ScheduleReadingComponent implements OnInit, OnDestroy {
  connection: Connection | null = null;
  interval: number = 0;
  tagValues: { tag: string; value: any; timestamp?: Date }[] = [];
  loading = true;
  errorMessage: string | null = null;
  lastUpdated: Date | null = null;
  saveStatus: 'idle' | 'saving' | 'success' | 'error' = 'idle';
  saveStatusMessage: string = '';

  private eventSource: EventSource | null = null;
  private savedTags: string[] = [];

  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit(): void {
    const state = history.state;
    this.connection = state['connection'];
    this.interval = state['interval'] ?? 0;

    if (this.connection) {
      this.fetchSavedTags();
    } else {
      this.router.navigate(['/']);
    }
  }

  ngOnDestroy(): void {
    this.closeEventSource();
  }

  private closeEventSource(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  fetchSavedTags(): void {
    if (!this.connection) return;

    const connectionId = this.connection.id;
    this.http.get<string[]>(`http://localhost:8081/getSavedTagsById?connectionId=${connectionId}`)
      .subscribe({
        next: (tags) => {
          if (tags.length > 0) {
            this.savedTags = tags;
            this.startSSEConnection(tags);
          } else {
            this.loading = false;
            this.tagValues = [];
          }
        },
        error: () => {
          this.loading = false;
          this.errorMessage = 'Failed to load saved tags.';
        }
      });
  }

  private startSSEConnection(tags: string[]): void {
    if (!this.connection) return;

    this.closeEventSource();
    
    const tagsParam = encodeURIComponent(tags.join(','));
    const url = `http://localhost:8083/getTagValuesByInterval?ip=${this.connection.ipAddress}&interval=${this.interval}&tags=${tagsParam}`;

    this.loading = true;
    this.errorMessage = null;

    this.eventSource = new EventSource(url);

    this.eventSource.addEventListener('message', (event) => {
      try {
        // Remove the "data: " prefix if present
        const dataStr = event.data.startsWith('data: ') ? event.data.substring(6) : event.data;
        const response = JSON.parse(dataStr);

        if (response.error) {
          this.handleError(response.message || 'Server error');
          return;
        }

        // Update UI with new values
        this.tagValues = Object.entries(response.data).map(([tag, value]) => ({
          tag,
          value: value !== null ? value : 'N/A',
          timestamp: new Date(response.timestamp)
        }));
        
        this.lastUpdated = new Date();
        this.loading = false;

        // Send data to save endpoint
        this.saveDataToDatabase({
          connectionId: this.connection?.id,
          //ipAddress: this.connection?.ipAddress,
          tagValues: this.tagValues,
          timestamp: response.timestamp
        });

      } catch (e) {
        console.error('Error parsing SSE data:', e);
        this.handleError('Error processing data from server');
      }
    });

    this.eventSource.addEventListener('error', () => {
      if (!this.errorMessage) {
        this.handleError('Connection to server failed');
      }
      this.closeEventSource();
    });
  }

  private saveDataToDatabase(data: any): void {
    this.saveStatus = 'saving';
    this.saveStatusMessage = 'Saving data...';

    this.http.post<{status: string, message: string}>('http://localhost:8081/tagValues/save', data)
      .subscribe({
        next: (response) => {
          this.saveStatus = 'success';
          this.saveStatusMessage = response.message || 'Data saved successfully!';
          setTimeout(() => this.resetSaveStatus(), 3000);
        },
        // error: (err) => {
        //   console.error('Error saving data:', err);
        //   this.saveStatus = 'error';
        //   this.saveStatusMessage = err.error?.message || 'Failed to save data!';
        //   setTimeout(() => this.resetSaveStatus(), 3000);
        // }
        error: (err) => {
            console.error('Error saving data:', err);
            this.saveStatus = 'error';
            
            // Try to get the error message from different parts of the error response
            const errorMessage = err.error?.message || 
                                err.error?.error || 
                                err.message || 
                                'Failed to save data!';
            
            this.saveStatusMessage = errorMessage;
            setTimeout(() => this.resetSaveStatus(), 3000);
        }
      });
  }

  private resetSaveStatus(): void {
    this.saveStatus = 'idle';
    this.saveStatusMessage = '';
  }

  private handleError(message: string): void {
    this.errorMessage = message;
    this.loading = false;
    this.closeEventSource();
  }

  goBack(): void {
    this.router.navigate(['/scheduler']);
  }
}