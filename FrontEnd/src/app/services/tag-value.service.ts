// import { Injectable } from '@angular/core';

// @Injectable({
//   providedIn: 'root'
// })
// export class TagValueService {

//   constructor() { }
// }
// // 

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { TagValueSaveRequest, ApiResponse } from '../models/tag-payload.model';
import { Observable } from 'rxjs';

export interface TagValueResponse {
  connectionId: number;
  timestamp: string;
  tagValues: { [key: string]: any };
}

export interface PaginatedResponse<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  number: number; // current page
  size: number;   // page size
}

@Injectable({
  providedIn: 'root'
})
export class TagValueService {
  private readonly baseUrl = 'http://localhost:8081'; // Adjust as needed

  constructor(private http: HttpClient) {}

  getTagValuesByConnection(connectionId: number, page: number = 0, size: number = 11): Observable<PaginatedResponse<TagValueResponse>> {
    const params = new HttpParams()
      .set('connectionId', connectionId.toString())
      .set('page', page.toString())
      .set('size', size.toString());

    return this.http.get<PaginatedResponse<TagValueResponse>>(`${this.baseUrl}/tagValues/byConnection`, { params });
  }

  saveTagValues(payload: TagValueSaveRequest): Observable<ApiResponse> {
    return this.http.post<ApiResponse>('http://localhost:8081/tagValues/saveBatch', payload);
  }


}
