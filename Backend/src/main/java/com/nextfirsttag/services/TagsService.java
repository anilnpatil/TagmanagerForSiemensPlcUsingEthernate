package com.nextfirsttag.services;

import com.nextfirsttag.entities.SelectedTag;
import com.nextfirsttag.exceptions.TagNotFoundException;

import java.util.List;
import java.util.Map;

public interface TagsService {
    Map<String, List<String>> getAllTags() throws TagNotFoundException;
    void saveSelectedTags(List<String> selectedTags, Long connectionId) throws RuntimeException;
    List<SelectedTag> getSavedTags() throws TagNotFoundException;
    List<String> getSavedTags(Long connectionId) throws TagNotFoundException;
    void deleteTags(List<String> tags, Long connectionId) throws RuntimeException;
    List<String>getSavedTagsByName(String ConnectionName) throws TagNotFoundException;
    String getIpAddressByConnectionName(String connectionName);
}
