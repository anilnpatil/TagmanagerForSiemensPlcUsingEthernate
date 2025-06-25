import { Component, OnInit } from '@angular/core';
import { Connection } from '../models/connection.model';
import { Router } from '@angular/router';
import { TagValueService, TagValueResponse } from '../services/tag-value.service';

@Component({
  selector: 'app-tag-value-history',
  templateUrl: './tag-value-history.component.html',
  styleUrls: ['./tag-value-history.component.scss']
})
export class TagValueHistoryComponent implements OnInit {
  connection: Connection | null = null;
  tagData: TagValueResponse[] = [];
  loading: boolean = false;

  currentPage = 0;
  pageSize = 11;
  totalElements = 0;

  constructor(
    private router: Router,
    private tagValueService: TagValueService
  ) {
    const nav = this.router.getCurrentNavigation();
    if (nav?.extras.state?.['connection']) {
      this.connection = nav.extras.state['connection'];
    } else {
      const stored = localStorage.getItem('selectedConnection');
      if (stored) {
        this.connection = JSON.parse(stored);
      }
    }
  }

  ngOnInit(): void {
    if (!this.connection?.id) {
      this.router.navigate(['/']);
      return;
    }
    this.loadData();
  }

  loadData(): void {
    this.loading = true;
    this.tagValueService.getTagValuesByConnection(this.connection!.id, this.currentPage, this.pageSize).subscribe({
      next: (res) => {
        this.tagData = res.content;
        this.totalElements = res.totalElements;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        // optionally show a toast or message
      }
    });
  }

    getTagKeys(tag: TagValueResponse): string[] {
    return tag ? Object.keys(tag.tagValues) : [];
  }

  totalPages(): number {
    return Math.ceil(this.totalElements / this.pageSize);
  }

  onPageChange(newPage: number): void {
    this.currentPage = newPage;
    this.loadData();
  }

  goBack(): void {
    this.router.navigate(['/scheduler'], {
      state: {
        connection: this.connection
      }
    });
  }
}
