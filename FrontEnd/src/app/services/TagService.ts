import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Tag } from '../models/Tag ';

@Injectable({
  providedIn: 'root'
})
export class TagService {
  private baseUrl = 'http://localhost:8080/api/tags';

  constructor(private http: HttpClient) {}

  getTagsByConnectionId(connectionId: number): Observable<Tag[]> {
    return this.http.get<Tag[]>(`${this.baseUrl}/connection/${connectionId}`);
  }

  saveTag(tag: Tag): Observable<Tag> {
    return this.http.post<Tag>(this.baseUrl, tag);
  }

  deleteTags(tagIds: number[]): Observable<void> {
    return this.http.request<void>('delete', this.baseUrl, { body: tagIds });
  }
}
