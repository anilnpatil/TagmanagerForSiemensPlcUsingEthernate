import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TagValueHistoryComponent } from './tag-value-history.component';

describe('TagValueHistoryComponent', () => {
  let component: TagValueHistoryComponent;
  let fixture: ComponentFixture<TagValueHistoryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TagValueHistoryComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TagValueHistoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
