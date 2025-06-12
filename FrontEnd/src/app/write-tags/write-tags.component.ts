// import { Component, OnInit } from '@angular/core';
// import { HttpClient } from '@angular/common/http';
// import { Router } from '@angular/router';
// import { Connection } from '../models/connection.model';

// @Component({
//   selector: 'app-write-tags',
//   templateUrl: './write-tags.component.html',
//   styleUrls: ['./write-tags.component.scss']
// })
// export class WriteTagsComponent implements OnInit {
//   tags: { tag: string, value: any }[] = [];
//   selectedTags: { tag: string, value: any }[] = [];
//   connection: Connection | null = null;
//   message: string = '';
//   messageType: string = '';
//   loading: boolean = false;

//   constructor(private http: HttpClient, private router: Router) {}

//   ngOnInit(): void {
//     const storedConnection = localStorage.getItem('selectedConnection');
//     if (storedConnection) {
//       this.connection = JSON.parse(storedConnection);
//       this.fetchSavedTags();
//     } else {
//       this.router.navigate(['/']);
//     }
//   }

//   fetchSavedTags() {
//     if (!this.connection) return;

//     const url = `http://localhost:8081/getSavedTagsById?connectionId=${this.connection.id}`;
//     this.http.get<string[]>(url).subscribe({
//       next: (savedTags) => {
//         this.tags = savedTags.map(tag => ({ tag, value: '' }));
//       },
//       error: () => {
//         this.showMessage('No Tags found', 'error');
//       }
//     });
//   }

//   writeTags() {
//     if (!this.connection || this.selectedTags.length === 0) return;

//     const url = `http://localhost:8083/insertDataToPlc?ip=${this.connection.ipAddress}`;
//     this.loading = true;
//     this.message = ''; // Clear any previous message

//     this.http.post<{ message: string }>(url, this.selectedTags).subscribe({
//       next: (response) => {
//         this.loading = false;

//         // Show success message
//         this.showMessage(response.message || 'Tags written successfully', 'success');

//         // Clear tag values and selected tags
//         this.tags.forEach(tag => (tag.value = ''));
//         this.selectedTags = [];
//       },
//       error: () => {
//         this.loading = false;
//         this.showMessage('Failed to write tag values', 'error');
//       }
//     });
//   }

//   showMessage(message: string, type: string) {
//     this.message = message;
//     this.messageType = type;

//     // Automatically hide the message after 3 seconds
//     setTimeout(() => {
//       this.message = '';
//       this.messageType = '';
//     }, 3000);
//   }

//   canWriteTags(): boolean {
//     return this.tags.some(tag => tag.value && tag.value.trim() !== '');
//   }

//   selectTagForWriting(tag: { tag: string, value: any }) {
//     const existingTag = this.selectedTags.find(t => t.tag === tag.tag);
//     if (existingTag) {
//       existingTag.value = tag.value;
//     } else {
//       this.selectedTags.push(tag);
//     }
//   }

//   goBack() {
//     this.router.navigate(['/tag-manager']);
//   }
// }

import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Connection } from '../models/connection.model';

@Component({
  selector: 'app-write-tags',
  templateUrl: './write-tags.component.html',
  styleUrls: ['./write-tags.component.scss']
})
export class WriteTagsComponent implements OnInit {
  tags: { tag: string, value: any, response?: any }[] = [];
  selectedTags: { tag: string, value: any }[] = [];
  connection: Connection | null = null;
  message: string = '';
  messageType: string = '';
  loading: boolean = false;

  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit(): void {
    const storedConnection = localStorage.getItem('selectedConnection');
    if (storedConnection) {
      this.connection = JSON.parse(storedConnection);
      this.fetchSavedTags();
    } else {
      this.router.navigate(['/']);
    }
  }

  fetchSavedTags() {
    if (!this.connection) return;

    const url = `http://localhost:8081/getSavedTagsById?connectionId=${this.connection.id}`;
    this.http.get<string[]>(url).subscribe({
      next: (savedTags) => {
        this.tags = savedTags.map(tag => ({ tag, value: '' }));
      },
      error: () => {
        this.showMessage('No Tags found', 'error');
      }
    });
  }

  writeTags() {
    if (!this.connection || this.selectedTags.length === 0) return;
  
    const url = `http://localhost:8083/insertDataToPlc?ip=${this.connection.ipAddress}`;
    this.loading = true;
    this.message = ''; // Clear any previous message
  
    // Clear previous responses
    this.tags.forEach(tag => delete tag.response);
  
    this.http.post<{ data: any, message: string }>(url, this.selectedTags).subscribe({
      next: (response) => {
        this.loading = false;
  
        // Update each tag with its response data
        if (response.data) {
          this.tags.forEach(tag => {
            if (response.data[tag.tag]) {
              tag.response = response.data[tag.tag];
            }
            // Clear the input field after writing
            tag.value = '';
          });
        }
  
        // Clear selected tags
        this.selectedTags = [];
  
        // Show success message
        this.showMessage(response.message || 'Tags written successfully', 'success');
      },
      error: () => {
        this.loading = false;
        this.showMessage('Failed to write tag values', 'error');
      }
    });
  }

  showMessage(message: string, type: string) {
    this.message = message;
    this.messageType = type;

    // Automatically hide the message after 3 seconds
    setTimeout(() => {
      this.message = '';
      this.messageType = '';
    }, 3000);
  }

  canWriteTags(): boolean {
    return this.tags.some(tag => tag.value && tag.value.trim() !== '');
  }

  selectTagForWriting(tag: { tag: string, value: any }) {
    const existingTag = this.selectedTags.find(t => t.tag === tag.tag);
    if (existingTag) {
      existingTag.value = tag.value;
    } else {
      this.selectedTags.push(tag);
    }
  }

  goBack() {
    this.router.navigate(['/tag-manager']);
  }
}