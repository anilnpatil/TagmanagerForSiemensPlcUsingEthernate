package com.nextfirsttag.services;

import com.nextfirsttag.dto.TagValueSaveRequest;

public interface TagValueLogService {
  void saveAll(TagValueSaveRequest request);
}
