import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AutoWriteTagsComponent } from './auto-write-tags.component';

describe('AutoWriteTagsComponent', () => {
  let component: AutoWriteTagsComponent;
  let fixture: ComponentFixture<AutoWriteTagsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AutoWriteTagsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AutoWriteTagsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
