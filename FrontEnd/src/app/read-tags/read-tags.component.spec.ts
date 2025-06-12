import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReadTagsComponent } from './read-tags.component';

describe('ReadTagsComponent', () => {
  let component: ReadTagsComponent;
  let fixture: ComponentFixture<ReadTagsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ReadTagsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ReadTagsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
