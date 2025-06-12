package com.nextfirsttag.services;

import com.nextfirsttag.dto.TagValueRequest;
import com.nextfirsttag.dto.TagValueResponse;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

public interface TagValueService {
    void saveTagValues(TagValueRequest request);
    Page<TagValueResponse> getTagValuesByConnection(Long connectionId, Pageable pageable);

}
