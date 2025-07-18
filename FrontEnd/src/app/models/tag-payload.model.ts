// export interface TagPayload {
// }

export interface TagValueEntry {
  name: string;
  value: any;
}

export interface IntervalTagGroup {
  interval: number;
  tags: TagValueEntry[];
}

export interface TagValueSaveRequest {
  connectionId: number;
  timestamp: string; // ISO format
  intervalTagValues: IntervalTagGroup[];
}

export interface ApiResponse {
  status: string;
  message: string;
}
