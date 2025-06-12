import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiResponse } from './models/api-response.model';
@Injectable({ providedIn: 'root' })
export class AuthService {
  private baseUrl = 'http://localhost:8081/auth';
  

  constructor(private http: HttpClient) {}

  
  register(user: { username: string; password: string; role: string }): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.baseUrl}/register`, user);
  }


  login(credentials: any) {
    return this.http.post(`${this.baseUrl}/login`, credentials);
  }

  saveToken(token: string) {
    localStorage.setItem('token', token);
  }

  getToken() {
    return localStorage.getItem('token');
  }

  logout() {
    localStorage.removeItem('token');
  }

  decodeToken(): any {
    const token = this.getToken();
    if (!token) return null;
    const payload = token.split('.')[1];
    return JSON.parse(atob(payload));
  }

  getRole(): string {
    const decoded = this.decodeToken();
    return decoded?.role || '';
  }
}