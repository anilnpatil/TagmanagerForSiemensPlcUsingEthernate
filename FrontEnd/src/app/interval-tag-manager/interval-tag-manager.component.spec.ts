import { ComponentFixture, TestBed } from '@angular/core/testing';

import { IntervalTagManagerComponent } from './interval-tag-manager.component';

describe('IntervalTagManagerComponent', () => {
  let component: IntervalTagManagerComponent;
  let fixture: ComponentFixture<IntervalTagManagerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ IntervalTagManagerComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(IntervalTagManagerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
