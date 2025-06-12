import { TestBed } from '@angular/core/testing';

import { ConnectionService } from './services/connection.service';

describe('ConnectionService', () => {
  let service: ConnectionService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ConnectionService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
