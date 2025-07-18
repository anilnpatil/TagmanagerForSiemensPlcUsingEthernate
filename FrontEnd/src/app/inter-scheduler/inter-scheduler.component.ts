// // inter-scheduler.component.ts
// import { Component, OnDestroy, OnInit } from '@angular/core';
// import { Router } from '@angular/router';
// import { Subscription } from 'rxjs';
// import { TagMonitorService } from '../services/tag-monitor.service';
// import { Connection } from '../models/connection.model';

// @Component({
//   selector: 'app-inter-scheduler',
//   templateUrl: './inter-scheduler.component.html',
//   styleUrls: ['./inter-scheduler.component.scss']
// })
// export class InterSchedulerComponent implements OnInit, OnDestroy {
//   connection: Connection | null = null;
//   activeInterval: number | null = null;
//   private subscription!: Subscription;

//   dynamicIntervals: any[] = [
//     { value: 1, customValue: 1 },
//     { value: 2, customValue: 2 },
//     { value: 3, customValue: 3 },
//     { value: 4, customValue: 4 },
//     { value: 5, customValue: 5 },
//     { value: 6, customValue: 6 }
//   ];

//   presetIntervals: number[] = [0.5, 1, 2, 3, 4, 5, 6, 10, 15, 30, 60];

//   constructor(
//     private router: Router,
//     private tagMonitorService: TagMonitorService
//   ) {
//     const navigation = this.router.getCurrentNavigation();
//     const stateConn = navigation?.extras?.state?.['connection'];

//     if (stateConn) {
//       this.connection = stateConn;
//       localStorage.setItem('selectedConnection', JSON.stringify(stateConn));
//     } else {
//       const storedConn = localStorage.getItem('selectedConnection');
//       if (storedConn) {
//         this.connection = JSON.parse(storedConn);
//       }
//     }

//     const storedActiveInterval = localStorage.getItem('activeInterval');
//     if (storedActiveInterval) {
//       this.activeInterval = parseFloat(storedActiveInterval);
//     }
//   }

//   ngOnInit(): void {
//     this.subscription = this.tagMonitorService.activeInterval$.subscribe(interval => {
//       this.activeInterval = typeof interval === 'string' ? Number(interval) : interval;
//       if (this.activeInterval != null) {
//         localStorage.setItem('activeInterval', this.activeInterval.toString());
//       } else {
//         localStorage.removeItem('activeInterval');
//       }
//     });
//   }

//   ngOnDestroy(): void {
//     if (this.subscription) {
//       this.subscription.unsubscribe();
//     }
//   }

//   getCurrentIntervalValue(interval: any): number {
//     return Number(interval.value === 'custom' ? interval.customValue : interval.value);
//   }

//   isValidInterval(value: number): boolean {
//     return value !== null && value !== undefined && value >= 0.1;
//   }

//   onIntervalChange(): void {
//     // No need to persist dynamicIntervals since they are fixed
//   }

//   goToScheduleReading(interval: number): void {
//     interval = Number(interval);
//     if (!this.connection || !this.isValidInterval(interval)) return;

//     this.activeInterval = interval;
//     localStorage.setItem('activeInterval', interval.toString());
//     localStorage.setItem('selectedConnection', JSON.stringify(this.connection));
//     localStorage.setItem('selectedInterval', interval.toString());

//     this.router.navigate(['/schedule-reading'], {
//       state: {
//         connection: this.connection,
//         interval: interval
//       }
//     });
//   }

//   goToAutoWrite(): void {
//     this.router.navigate(['/auto-write-tags']);
//   }

//   goToViewHistory(): void {
//     if (this.connection) {
//       this.router.navigate(['/tag-value-history'], {
//         state: { connection: this.connection }
//       });
//     }
//   }

//   goToScheduleBuilder(): void {
//     this.router.navigate(['/schedule-builder']);
//   }

//   goBack(): void {
//     this.router.navigate(['/tag-manager']);
//   }
//   openManageTags(intervalValue: number): void {
//   if (!this.connection) return;

//   // Get actual current value of the interval (custom or preset)
//   const matchedInterval = this.dynamicIntervals.find(interval =>
//     this.getCurrentIntervalValue(interval) === intervalValue
//   );

//   const actualInterval = matchedInterval ? this.getCurrentIntervalValue(matchedInterval) : intervalValue;

//   localStorage.setItem('intervalConnection', JSON.stringify(this.connection));
//   localStorage.setItem('selectedInterval', actualInterval.toString());

//   this.router.navigate(['/interval-tag-manager'], {
//     state: {
//       connection: this.connection,
//       interval: actualInterval
//     }
//   });
// }

// }

import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { TagMonitorService } from '../services/tag-monitor.service';
import { Connection } from '../models/connection.model';

@Component({
  selector: 'app-inter-scheduler',
  templateUrl: './inter-scheduler.component.html',
  styleUrls: ['./inter-scheduler.component.scss']
})
export class InterSchedulerComponent implements OnInit, OnDestroy {
  connection: Connection | null = null;
  activeInterval: number | null = null;
  private subscription!: Subscription;

  dynamicIntervals: any[] = [
    { value: 1, customValue: 1 },
    { value: 2, customValue: 2 },
    { value: 3, customValue: 3 },
    { value: 4, customValue: 4 },
    { value: 5, customValue: 5 },
    { value: 6, customValue: 6 }
  ];

  presetIntervals: number[] = [0.5, 1, 2, 3, 4, 5, 6, 10, 15, 30, 60];

  constructor(
    private router: Router,
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

    const storedActiveInterval = localStorage.getItem('activeInterval');
    if (storedActiveInterval) {
      this.activeInterval = parseFloat(storedActiveInterval);
    }
  }

  ngOnInit(): void {
    // Load interval settings from localStorage
    const savedIntervals = localStorage.getItem('dynamicIntervals');
    if (savedIntervals) {
      try {
        this.dynamicIntervals = JSON.parse(savedIntervals);
      } catch (e) {
        console.error('Error parsing saved intervals:', e);
      }
    }

    // Watch active interval
    this.subscription = this.tagMonitorService.activeInterval$.subscribe(interval => {
      this.activeInterval = typeof interval === 'string' ? Number(interval) : interval;
      if (this.activeInterval != null) {
        localStorage.setItem('activeInterval', this.activeInterval.toString());
      } else {
        localStorage.removeItem('activeInterval');
      }
    });
  }

  ngOnDestroy(): void {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  getCurrentIntervalValue(interval: any): number {
    return Number(interval.value === 'custom' ? interval.customValue : interval.value);
  }

  isValidInterval(value: number): boolean {
    return value !== null && value !== undefined && value >= 0.1;
  }

  onIntervalChange(): void {
    localStorage.setItem('dynamicIntervals', JSON.stringify(this.dynamicIntervals));
  }

  goToScheduleReading(interval: number): void {
    interval = Number(interval);
    if (!this.connection || !this.isValidInterval(interval)) return;

    this.activeInterval = interval;
    localStorage.setItem('activeInterval', interval.toString());
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
        state: { connection: this.connection }
      });
    }
  }

  goToScheduleBuilder(): void {
    this.router.navigate(['/schedule-builder']);
  }

  goBack(): void {
    this.router.navigate(['/tag-manager']);
  }

  openManageTags(interval: number): void {
    if (!this.connection) return;

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
