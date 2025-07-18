import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import { Connection } from '../models/connection.model';

@Component({
  selector: 'app-interval-tag-manager',
  templateUrl: './interval-tag-manager.component.html',
  styleUrls: ['./interval-tag-manager.component.scss']
})
export class IntervalTagManagerComponent implements OnInit {
  availableTags: string[] = []; // Tags from global selection (left side)
  intervalTags: string[] = [];  // Tags selected for interval (right side)
  selectedTags: string[] = [];  // Currently selected tags (from either box)
  savedTags: string[] = [];     // Tags saved to backend
  newTags: string[] = [];       // Tags added in this session
  fromAvailable: boolean = true;
  message: string = '';
  messageType: string = '';
  connection: Connection | null = null;
  interval: number = 0;

  constructor(
    private http: HttpClient,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  // ngOnInit(): void {
  //   const state = history.state;
  //   this.connection = state.connection || JSON.parse(localStorage.getItem('selectedConnection') || '{}');
  //   // this.interval = state.interval || parseInt(localStorage.getItem('selectedInterval') || '0');
  //   if (state.interval) {
  //     this.interval = state.interval;
  //     localStorage.setItem('selectedInterval', this.interval.toString());
  //   } else {
  //     this.interval = parseInt(localStorage.getItem('selectedInterval') || '0');
  //   }

  //   if (!this.connection || !this.connection.id) {
  //     this.router.navigate(['/']);
  //     return;
  //   }

  //   this.fetchTags(this.connection);
  // }

  ngOnInit(): void {
  const state = history.state;
  this.connection = state.connection || JSON.parse(localStorage.getItem('selectedConnection') || '{}');

  if (state.interval !== undefined && state.interval !== null) {
    this.interval = parseFloat(state.interval);
    localStorage.setItem('selectedInterval', this.interval.toString());
  } else {
    this.interval = parseFloat(localStorage.getItem('selectedInterval') || '0');
  }

  if (!this.connection || !this.connection.id) {
    this.router.navigate(['/']);
    return;
  }

  this.fetchTags(this.connection);
}


  fetchTags(connection: Connection): void {
    this.http.get<string[]>(`http://localhost:8081/getSavedTagsById?connectionId=${connection.id}`).subscribe({
      next: globalTags => {
        this.http.get<string[]>(`http://localhost:8081/interval-tags/get?connectionId=${connection.id}&interval=${this.interval}`).subscribe({
          next: intervalTags => {
            this.savedTags = intervalTags;
            this.intervalTags = [...intervalTags];
            this.availableTags = globalTags.filter(tag => !intervalTags.includes(tag));
            this.updateNewTags();
            this.updateButtonGlow();
          },
          error: error => {
            const errorMessage = error?.error?.message || 'Failed to fetch interval tags';
            this.showMessage(errorMessage, 'error');
            this.intervalTags = [];
            this.savedTags = [];
            this.availableTags = globalTags;
          }
        });
      },
      error: error => {
        const errorMessage = error?.error?.message || 'Failed to fetch global tags';
        this.showMessage(errorMessage, 'error');
        this.intervalTags = [];
        this.savedTags = [];
        this.availableTags = [];
      }
    });
  }

  selectTag(tag: string, event: MouseEvent, fromRightBox: boolean): void {
    if (event.ctrlKey) {
      if (this.selectedTags.includes(tag)) {
        this.selectedTags = this.selectedTags.filter(t => t !== tag);
      } else {
        this.selectedTags.push(tag);
      }
    } else {
      this.selectedTags = [tag];
    }
    this.fromAvailable = !fromRightBox;
  }

  moveSelectedTags(toRight: boolean): void {
    if (toRight && this.fromAvailable) {
      const moving = this.selectedTags.filter(tag => this.availableTags.includes(tag));
      this.intervalTags.push(...moving);
      this.availableTags = this.availableTags.filter(tag => !moving.includes(tag));
    } else if (!toRight && !this.fromAvailable) {
      const moving = this.selectedTags.filter(tag => this.intervalTags.includes(tag));
      this.availableTags.push(...moving);
      this.intervalTags = this.intervalTags.filter(tag => !moving.includes(tag));
      this.deleteTagsFromDatabase(moving);
    }
    this.selectedTags = [];
    this.updateNewTags();
    this.updateButtonGlow();
  }

  deleteTagsFromDatabase(tags: string[]): void {
    const connectionId = this.connection?.id;
    if (!connectionId) return;

    this.http.request<{ message: string }>('delete', `http://localhost:8081/interval-tags/delete-specific?connectionId=${connectionId}&interval=${this.interval}`, {
      body: { tags }
    }).subscribe({
      next: () => {
        this.showMessage('Tags deleted from interval successfully', 'success');
        this.fetchTags(this.connection!);
      },
      error: error => {
        const errorMessage = error?.error?.message || 'Error deleting tags from interval';
        this.showMessage(errorMessage, 'error');
      }
    });
  }

  updateNewTags(): void {
    this.newTags = this.intervalTags.filter(tag => !this.savedTags.includes(tag));
  }

  isMoveToRightAllowed(): boolean {
    return this.fromAvailable && this.selectedTags.some(tag => this.availableTags.includes(tag));
  }

  isMoveToLeftAllowed(): boolean {
    return !this.fromAvailable && this.selectedTags.some(tag => this.intervalTags.includes(tag));
  }

  saveSelectedTags(): void {
    if (!this.connection || this.newTags.length === 0) return;

    const payload = {
      connectionId: this.connection.id,
      interval: this.interval,
      tags: this.newTags
    };

    this.http.post(`http://localhost:8081/interval-tags/save`, payload).subscribe({
      next: (response: any) => {
        this.showMessage(response?.message || 'Tags saved successfully', 'success');
        this.fetchTags(this.connection!);
      },
      error: error => {
        const errorMessage = error?.error?.message || 'Error saving tags';
        this.showMessage(errorMessage, 'error');
      }
    });
  }

  clearSelectedTags(): void {
    this.intervalTags = [...this.savedTags];
    this.availableTags = [...this.availableTags, ...this.newTags];
    this.newTags = [];
    this.selectedTags = [];
    this.updateButtonGlow();
  }
  
  goToScheduler(): void {
   this.router.navigate(['/inter-scheduler']);
  }

  isNewTag(tag: string): boolean {
    return this.newTags.includes(tag);
  }

  updateButtonGlow(): void {
    const okBtn = document.querySelector('.bottom-controls .ok') as HTMLButtonElement;
    const cancelBtn = document.querySelector('.bottom-controls .cancel') as HTMLButtonElement;
    if (!okBtn || !cancelBtn) return;

    const hasNewTags = this.newTags.length > 0;

    okBtn.disabled = !hasNewTags;
    cancelBtn.disabled = !hasNewTags;

    okBtn.classList.toggle('glow-green', hasNewTags);
    cancelBtn.classList.toggle('glow-yellow', hasNewTags);
  }

  showMessage(message: string, type: string): void {
    this.message = message;
    this.messageType = type;
    setTimeout(() => {
      this.message = '';
      this.messageType = '';
    }, 3000);
  }

  goToHome(): void {
    this.router.navigate(['/home1']);
  }
}
