import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InterSchedulerComponent } from './inter-scheduler.component';

describe('InterSchedulerComponent', () => {
  let component: InterSchedulerComponent;
  let fixture: ComponentFixture<InterSchedulerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ InterSchedulerComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(InterSchedulerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
