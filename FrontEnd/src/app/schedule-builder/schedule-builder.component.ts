// // schedule-builder.component.ts
// import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
// import { HttpClient } from '@angular/common/http';
// import { FormControl } from '@angular/forms';
// import { Location } from '@angular/common';

// interface TagGroup {
//   interval: number;
//   tags: string[];
// }

// @Component({
//   selector: 'app-schedule-builder',
//   templateUrl: './schedule-builder.component.html',
//   styleUrls: ['./schedule-builder.component.scss']
// })
// export class ScheduleBuilderComponent implements OnInit, OnDestroy {
//   connectionId = 1;
//   intervalTagGroups: TagGroup[] = [];
//   callFrequencyHzControl = new FormControl(2);
//   currentPayload: string[] = [];
//   timerId: any;
//   startTimestamp: number = 0;
//   latestData: any[] = [];
//   showIntervalGroup = false;
//   currentYear: number = new Date().getFullYear();
//   alreadyTriggeredIntervals: Set<number> = new Set();
//   errorMessage: string | null = null;
//   fixedDisplayGroups: TagGroup[] = new Array(6).fill(null).map((_, index) => ({ interval: index + 1, tags: [] }));

//   @ViewChild('dataTableWrapper') dataTableWrapper!: ElementRef<HTMLDivElement>;

//   constructor(private http: HttpClient, private location: Location) {}

//   ngOnInit(): void {
//     this.callFrequencyHzControl.valueChanges.subscribe(() => this.restartScheduler());
//     this.fetchAndPrepareSchedule();
//   }

//   fetchAndPrepareSchedule(): void {
//     this.intervalTagGroups = [];
//     this.currentPayload = [];
//     this.latestData = [];
//     this.errorMessage = null;
//     this.alreadyTriggeredIntervals.clear();
//     if (this.timerId) clearInterval(this.timerId);

//     this.http.get<TagGroup[]>(`http://localhost:8081/interval-tags/grouped?connectionId=${this.connectionId}`)
//       .subscribe({
//         next: groups => {
//           const sortedGroups = groups.sort((a, b) => a.interval - b.interval);
//           for (let i = 0; i < 6; i++) {
//             this.fixedDisplayGroups[i] = sortedGroups[i] || { interval: i + 1, tags: [] };
//           }
//           this.intervalTagGroups = sortedGroups;
//           this.startDynamicSchedule();
//         },
//         error: err => {
//           this.errorMessage = 'Failed to fetch interval groups.';
//           console.error(err);
//         }
//       });
//   }

//   restartScheduler(): void {
//     if (this.timerId) clearInterval(this.timerId);
//     this.alreadyTriggeredIntervals.clear();
//     this.startDynamicSchedule();
//   }

//   startDynamicSchedule(): void {
//     this.startTimestamp = Date.now();
//     const frequency = this.callFrequencyHzControl.value || 2;
//     const intervalMs = 1000 / frequency;
//     this.timerId = setInterval(() => this.executeScheduler(), intervalMs);
//   }

//   executeScheduler(): void {
//     const elapsedSeconds = (Date.now() - this.startTimestamp) / 1000;

//     const dueGroups = this.intervalTagGroups.filter(group => {
//       return elapsedSeconds >= group.interval && !this.alreadyTriggeredIntervals.has(group.interval);
//     });

//     for (let group of dueGroups) {
//       this.currentPayload.push(...group.tags);
//       this.alreadyTriggeredIntervals.add(group.interval);
//     }

//     if (dueGroups.length > 0) {
//       const uniqueTags = [...new Set(this.currentPayload)];
//       this.makeBackendCall(uniqueTags);
//     }
//   }

//   makeBackendCall(tags: string[]): void {
//     const payload = { tags };
//     this.http.post<any>(`http://localhost:8083/getTagValues?ip=192.168.0.1`, payload)
//       .subscribe({
//         next: res => {
//           console.log('Payload sent at', new Date().toLocaleTimeString(), tags);
//           if (res?.data) {
//             const row: any = {};
//             for (const tag of tags) {
//               row[tag] = res.data[tag] !== undefined ? res.data[tag] : null;
//             }
//             this.latestData.push(row);
//             this.errorMessage = null;
//             this.autoScrollToBottom();
//           }
//         },
//         error: err => {
//           this.errorMessage = err.error?.message || 'Read failed.';
//           console.error('Error:', err);
//         }
//       });
//   }

//   autoScrollToBottom(): void {
//     setTimeout(() => {
//       if (this.dataTableWrapper) {
//         const el = this.dataTableWrapper.nativeElement;
//         el.scrollTop = el.scrollHeight;
//         el.scrollLeft = el.scrollWidth;
//       }
//     }, 100);
//   }

//   getTagHeaders(): string[] {
//     const headerSet = new Set<string>();
//     for (const row of this.latestData) {
//       Object.keys(row).forEach(key => headerSet.add(key));
//     }
//     return Array.from(headerSet).sort();
//   }

//   toggleIntervalGroup(): void {
//     this.showIntervalGroup = !this.showIntervalGroup;
//   }

//   getIntervalGroupButtonLabel(): string {
//     return this.showIntervalGroup ? 'Hide Interval Groups' : 'Show Interval Groups';
//   }

//   goBack(): void {
//     this.location.back();
//   }

//   ngOnDestroy(): void {
//     if (this.timerId) clearInterval(this.timerId);
//   }
// }

// schedule-builder.component.ts
// schedule-builder.component.ts
// schedule-builder.component.ts
import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormControl } from '@angular/forms';
import { Location } from '@angular/common';
import { TagValueService } from '../services/tag-value.service';
import { TagValueEntry, IntervalTagGroup, TagValueSaveRequest } from '../models/tag-payload.model';

interface TagGroup {
  interval: number;
  tags: string[];
}

@Component({
  selector: 'app-schedule-builder',
  templateUrl: './schedule-builder.component.html',
  styleUrls: ['./schedule-builder.component.scss']
})
export class ScheduleBuilderComponent implements OnInit, OnDestroy {
  connectionId = 1;
  intervalTagGroups: TagGroup[] = [];
  callFrequencyHzControl = new FormControl(2);
  currentPayload: string[] = [];
  timerId: any;
  startTimestamp: number = 0;
  latestData: any[] = [];
  showIntervalGroup = false;
  currentYear: number = new Date().getFullYear();
  alreadyTriggeredIntervals: Set<number> = new Set();
  errorMessage: string | null = null;
  fixedDisplayGroups: TagGroup[] = new Array(6).fill(null).map((_, index) => ({ interval: index + 1, tags: [] }));

  @ViewChild('dataTableWrapper') dataTableWrapper!: ElementRef<HTMLDivElement>;

  constructor(
    private http: HttpClient,
    private location: Location,
    private tagValueService: TagValueService
  ) {}

  ngOnInit(): void {
    this.callFrequencyHzControl.valueChanges.subscribe(() => this.restartScheduler());
    this.fetchAndPrepareSchedule();
  }

  fetchAndPrepareSchedule(): void {
    this.intervalTagGroups = [];
    this.currentPayload = [];
    this.latestData = [];
    this.errorMessage = null;
    this.alreadyTriggeredIntervals.clear();
    if (this.timerId) clearInterval(this.timerId);

    this.http.get<TagGroup[]>(`http://localhost:8081/interval-tags/grouped?connectionId=${this.connectionId}`)
      .subscribe({
        next: groups => {
          const sortedGroups = groups.sort((a, b) => a.interval - b.interval);
          for (let i = 0; i < 6; i++) {
            this.fixedDisplayGroups[i] = sortedGroups[i] || { interval: i + 1, tags: [] };
          }
          this.intervalTagGroups = sortedGroups;
          this.startDynamicSchedule();
        },
        error: err => {
          this.errorMessage = 'Failed to fetch interval groups.';
          console.error(err);
        }
      });
  }

  restartScheduler(): void {
    if (this.timerId) clearInterval(this.timerId);
    this.alreadyTriggeredIntervals.clear();
    this.startDynamicSchedule();
  }

  startDynamicSchedule(): void {
    this.startTimestamp = Date.now();
    const frequency = this.callFrequencyHzControl.value || 2;
    const intervalMs = 1000 / frequency;
    this.timerId = setInterval(() => this.executeScheduler(), intervalMs);
  }

  executeScheduler(): void {
    const elapsedSeconds = (Date.now() - this.startTimestamp) / 1000;

    const dueGroups = this.intervalTagGroups.filter(group => {
      return elapsedSeconds >= group.interval && !this.alreadyTriggeredIntervals.has(group.interval);
    });

    for (let group of dueGroups) {
      this.currentPayload.push(...group.tags);
      this.alreadyTriggeredIntervals.add(group.interval);
    }

    if (dueGroups.length > 0) {
      const uniqueTags = [...new Set(this.currentPayload)];
      this.makeBackendCall(uniqueTags);
    }
  }

  makeBackendCall(tags: string[]): void {
    const payload = { tags };
    const timestamp = new Date().toISOString();

    this.http.post<any>(`http://localhost:8083/getTagValues?ip=192.168.0.1`, payload)
      .subscribe({
        next: res => {
          console.log('Payload sent at', new Date().toLocaleTimeString(), tags);
          if (res?.data) {
            const row: any = {};
            const tagEntries: TagValueEntry[] = [];

            for (const tag of tags) {
              const value = res.data[tag] !== undefined ? res.data[tag] : null;
              row[tag] = value;
              tagEntries.push({ name: tag, value });
            }

            this.latestData.push(row);
            this.sendToLogger(tagEntries, timestamp);
            this.errorMessage = null;
            this.autoScrollToBottom();
          }
        },
        error: err => {
          this.errorMessage = err.error?.message || 'Read failed.';
          console.error('Error:', err);
        }
      });
  }

  sendToLogger(tagEntries: TagValueEntry[], timestamp: string): void {
    const intervalGroups: IntervalTagGroup[] = this.intervalTagGroups.map(group => {
      const matchedTags = tagEntries.filter(entry => group.tags.includes(entry.name));
      return {
        interval: group.interval,
        tags: matchedTags.map(entry => ({ name: entry.name, value: entry.value }))
      };
    }).filter(group => group.tags.length > 0);

    if (intervalGroups.length === 0) return;

    const logPayload: TagValueSaveRequest = {
      connectionId: this.connectionId,
      timestamp,
      intervalTagValues: intervalGroups
    };

    this.tagValueService.saveTagValues(logPayload).subscribe({
      next: res => console.log('Log Saved:', res.message),
      error: err => console.error('Log Save Failed:', err.error?.message || err.message)
    });
  }

  autoScrollToBottom(): void {
    setTimeout(() => {
      if (this.dataTableWrapper) {
        const el = this.dataTableWrapper.nativeElement;
        el.scrollTop = el.scrollHeight;
        el.scrollLeft = el.scrollWidth;
      }
    }, 100);
  }

  getTagHeaders(): string[] {
    const headerSet = new Set<string>();
    for (const row of this.latestData) {
      Object.keys(row).forEach(key => headerSet.add(key));
    }
    return Array.from(headerSet).sort();
  }

  toggleIntervalGroup(): void {
    this.showIntervalGroup = !this.showIntervalGroup;
  }

  getIntervalGroupButtonLabel(): string {
    return this.showIntervalGroup ? 'Hide Interval Groups' : 'Show Interval Groups';
  }

  goBack(): void {
    this.location.back();
  }

  ngOnDestroy(): void {
    if (this.timerId) clearInterval(this.timerId);
  }
}
