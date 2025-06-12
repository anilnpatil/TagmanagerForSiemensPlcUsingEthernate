import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Connection } from '../models/connection.model';

interface BackendResponse {
  data?: {
    [key: string]: TagResponse;
  };
  message?: string;
}

interface TagResponse {
  value_written?: any;
  data_type?: string;
  status?: string;
  message?: string;
}

interface Tag {
  tag: string;
  value: any;
  response?: TagResponse;
  isWriting: boolean;
}

@Component({
  selector: 'app-auto-write-tags',
  templateUrl: './auto-write-tags.component.html',
  styleUrls: ['./auto-write-tags.component.scss']
})
export class AutoWriteTagsComponent implements OnInit {
  tags: Tag[] = [];
  connection: Connection | null = null;
  message: string = '';
  messageType: string = '';
  globalLoading: boolean = false;

  constructor(private http: HttpClient, private router: Router) {}

   getTagResponseProperty(tag: Tag, property: keyof TagResponse): any {
    return tag.response ? tag.response[property] : undefined;
  }

  ngOnInit(): void {
    this.initializeConnection();
    if (this.connection) {
      this.fetchSavedTags();
    } else {
      this.router.navigate(['/']);
    }
  }

  private initializeConnection() {
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras?.state?.['connection']) {
      this.connection = navigation.extras.state['connection'];
    } else {
      const stored = localStorage.getItem('selectedConnection');
      if (stored) {
        this.connection = JSON.parse(stored);
      }
    }
  }

  fetchSavedTags() {
    if (!this.connection) return;

    const url = `http://localhost:8081/getSavedTagsById?connectionId=${this.connection.id}`;
    this.http.get<string[]>(url).subscribe({
      next: (savedTags) => {
        this.tags = savedTags.map(tag => ({ 
          tag, 
          value: '',
          isWriting: false
        }));
      },
      error: (error) => {
        this.showMessage(this.getErrorMessage(error), 'error');
      }
    });
  }

  onTagValueChange(tag: Tag, event: any) {
    if (event.type === 'blur' && tag.value && tag.value.trim() !== '') {
      this.writeSingleTag(tag);
    }
  }

  writeSingleTag(tag: Tag) {
    if (!this.connection || !tag.value || tag.value.trim() === '') return;

    const url = `http://localhost:8083/insertDataToPlc?ip=${this.connection.ipAddress}`;
    tag.isWriting = true;
    tag.response = undefined;

    this.http.post<BackendResponse>(url, [{ tag: tag.tag, value: tag.value }]).subscribe({
      next: (response) => {
        tag.isWriting = false;
        if (response.data && response.data[tag.tag]) {
          tag.response = response.data[tag.tag];
        }
        this.showMessage(response.message || `Tag ${tag.tag} written successfully`, 'success');
      },
      error: (error) => {
        tag.isWriting = false;
        tag.response = {
          status: 'Failed',
          message: this.getErrorMessage(error)
        };
        this.showMessage(this.getErrorMessage(error), 'error');
      }
    });
  }

  private getErrorMessage(error: any): string {
    if (error.error && error.error.message) {
      return error.error.message;
    } else if (error.message) {
      return error.message;
    }
    return 'An unknown error occurred';
  }

  showMessage(message: string, type: string) {
    this.message = message;
    this.messageType = type;
    setTimeout(() => {
      this.message = '';
      this.messageType = '';
    }, 5000); // Increased timeout to 5 seconds for better readability
  }

  goBack() {
    this.router.navigate(['/scheduler']);
  }
}