import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Connection } from '../models/connection.model'; // Adjust the import path based on your structure

@Component({
  selector: 'app-read-tags',
  templateUrl: './read-tags.component.html',
  styleUrls: ['./read-tags.component.scss']
})
export class ReadTagsComponent implements OnInit {
  connection: Connection | null = null;
  tagValues: { tag: string, value: any }[] = [];
  loading: boolean = true; // Add the loading property

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit(): void {
    const storedConnection = localStorage.getItem('selectedConnection');
    if (storedConnection) {
      this.connection = JSON.parse(storedConnection);
      if (this.connection) {
        this.fetchSavedTags();
      }
    } else {
      this.router.navigate(['/']); // Navigate back if no connection is found
    }
  }

  fetchSavedTags() {
    if (!this.connection) return;
    
    const connectionId = this.connection.id;
    this.http.get<string[]>(`http://localhost:8081/getSavedTagsById?connectionId=${connectionId}`)
      .subscribe({
        next: (tags) => {
          if (tags.length > 0) {
            this.fetchTagValues(tags);
          } else {
            this.loading = false; // No tags found
          }
        },
        error: () => {
          this.loading = false; // Handle error and stop loading
        }
      });
  }

  fetchTagValues(tags: string[]) {
    const tagUrl = `http://localhost:8083/getTagValues?ip=${this.connection?.ipAddress}`;
    
    this.http.post<{ [key: string]: any }>(tagUrl, { tags }).subscribe({
      next: (response) => {
        // Access 'data' property using bracket notation
        this.tagValues = Object.entries(response['data'] || {}).map(([tag, value]) => ({ tag, value }));
        this.loading = false; // Data loaded
      },
      error: () => {
        this.loading = false; // Handle error and stop loading
      }
    });
  }
    

  goBack(): void {
    this.router.navigate(['/tag-manager']); // Go back to the home or previous page
  }
}
