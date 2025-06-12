import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ScheduleReadingComponent } from './schedule-reading.component';

describe('ScheduleReadingComponent', () => {
  let component: ScheduleReadingComponent;
  let fixture: ComponentFixture<ScheduleReadingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ScheduleReadingComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ScheduleReadingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
