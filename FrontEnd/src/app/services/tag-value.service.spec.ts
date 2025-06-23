import { TestBed } from '@angular/core/testing';

import { TagValueService } from './tag-value.service';

describe('TagValueService', () => {
  let service: TagValueService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TagValueService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
