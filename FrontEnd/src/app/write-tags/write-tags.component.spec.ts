import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WriteTagsComponent } from './write-tags.component';

describe('WriteTagsComponent', () => {
  let component: WriteTagsComponent;
  let fixture: ComponentFixture<WriteTagsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WriteTagsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(WriteTagsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
