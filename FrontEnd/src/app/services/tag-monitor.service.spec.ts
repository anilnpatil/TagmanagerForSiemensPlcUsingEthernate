import { TestBed } from '@angular/core/testing';

import { TagMonitorService } from './tag-monitor.service';

describe('TagMonitorService', () => {
  let service: TagMonitorService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TagMonitorService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
