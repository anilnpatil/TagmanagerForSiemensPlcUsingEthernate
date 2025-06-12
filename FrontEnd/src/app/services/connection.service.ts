import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Connection } from '../models/connection.model';

@Injectable({
  providedIn: 'root'
})
export class ConnectionService {
  private baseUrl = 'http://localhost:8081/api'; // Adjust the base URL as needed

  constructor(private http: HttpClient) {}

  // Fetch all connections
  getConnections(): Observable<Connection[]> {
    return this.http.get<Connection[]>(`${this.baseUrl}/connections`);
  }

  // Add a new connection
  addConnection(connection: Connection): Observable<Connection> {
    return this.http.post<Connection>(`${this.baseUrl}/connections`, connection);
  }

  // Fetch tags associated with a specific connection
  getTagsByConnection(connection: Connection): Observable<string[]> {
    const params = new HttpParams()
      .set('ipAddress', connection.ipAddress)
      .set('name', connection.name)
      .set('gateway', connection.gateway)
      .set('subnet', connection.subnet);
    return this.http.get<string[]>(`${this.baseUrl}/readDataTagsFromPlc/${connection.id}`, { params });
  }

  // Delete a specific connection by ID
  deleteConnection(connectionId: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.baseUrl}/connections/${connectionId}`);
  }
}
