package com.nextfirsttag.services;

import java.util.List;

public interface IntervalTagService {
    void saveTagsForInterval(Long connectionId, int interval, List<String> tags);
    List<String> getTagsForInterval(Long connectionId, int interval);
    void deleteSpecificTagsForInterval(Long connectionId, int interval, List<String> tags);
    void deleteAllTagsForInterval(Long connectionId, int interval);
    
}
