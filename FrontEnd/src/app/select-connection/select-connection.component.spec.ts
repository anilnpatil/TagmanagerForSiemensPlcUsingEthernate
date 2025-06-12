import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SelectConnectionComponent } from './select-connection.component';

describe('SelectConnectionComponent', () => {
  let component: SelectConnectionComponent;
  let fixture: ComponentFixture<SelectConnectionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SelectConnectionComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SelectConnectionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
