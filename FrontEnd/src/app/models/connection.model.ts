// src/app/models/connection.model.ts

export interface Connection {
  id: number;
  name: string;
  ipAddress: string;
  subnet: string;
  gateway: string;
}