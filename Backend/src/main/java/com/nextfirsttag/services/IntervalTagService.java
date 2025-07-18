package com.nextfirsttag.services;

import java.util.List;

import com.nextfirsttag.dto.IntervalTagGroupDTO;

public interface IntervalTagService {
    void saveTagsForInterval(Long connectionId, Float interval, List<String> tags);
    List<String> getTagsForInterval(Long connectionId, Float interval);
    List<IntervalTagGroupDTO>getGroupedTagsByConnection(Long connectionId);
    void deleteSpecificTagsForInterval(Long connectionId, Float interval, List<String> tags);
    void deleteAllTagsForInterval(Long connectionId, Float interval);
    
}
