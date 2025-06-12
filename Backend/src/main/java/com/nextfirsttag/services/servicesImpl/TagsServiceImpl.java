package com.nextfirsttag.services.servicesImpl;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.nextfirsttag.entities.Connection;
import com.nextfirsttag.entities.SelectedTag;
import com.nextfirsttag.entities.Tags;
import com.nextfirsttag.exceptions.TagNotFoundException;
import com.nextfirsttag.repositories.ConnectionRepository;
import com.nextfirsttag.repositories.SelectedTagRepository;
import com.nextfirsttag.repositories.TagsRepository;
import com.nextfirsttag.services.TagsService;

@Service
public class TagsServiceImpl implements TagsService {
    private final TagsRepository tagRepository;
    private final SelectedTagRepository selectedTagRepository;
    private final ConnectionRepository connectionRepository;

    public TagsServiceImpl(TagsRepository tagRepository, SelectedTagRepository selectedTagRepository, ConnectionRepository connectionRepository) {
        this.tagRepository = tagRepository;
        this.selectedTagRepository = selectedTagRepository;
        this.connectionRepository = connectionRepository;
    }

    @Override
    public Map<String, List<String>> getAllTags() throws TagNotFoundException {
        List<Tags> tags = tagRepository.findAll();
        List<String> tagNames = tags.stream().map(Tags::getTag).collect(Collectors.toList());
        if (tagNames.isEmpty()) {
            throw new TagNotFoundException("No tags found");
        }
        Map<String, List<String>> response = new HashMap<>();
        response.put("tags", tagNames);
        return response;       
    }

    @Transactional
    @Override
    public void saveSelectedTags(List<String> selectedTags, Long connectionId) throws RuntimeException {
        try {
            Connection connection = connectionRepository.findById(connectionId).orElseThrow(() -> new RuntimeException("Connection not found"));
            List<SelectedTag> tags = selectedTags.stream()
                                                 .map(tag -> new SelectedTag(null, tag, connection))
                                                 .collect(Collectors.toList());
            selectedTagRepository.saveAll(tags);
        } catch (Exception e) {
            throw new RuntimeException("Failed to save tags to the database", e);
        }
    }

    @Override
    public List<SelectedTag> getSavedTags() throws TagNotFoundException {
        List<SelectedTag> savedTags = selectedTagRepository.findAll();
        if (savedTags.isEmpty()) {
            throw new TagNotFoundException("No saved tags found");
        }
        return savedTags;
    }

    @Override
    public List<String> getSavedTags(Long connectionId) throws TagNotFoundException {
        List<SelectedTag> savedTags = selectedTagRepository.findByConnectionId(connectionId);
        if (savedTags.isEmpty()) {
            throw new TagNotFoundException("No saved tags found for the connection");
        }
        return savedTags.stream().map(SelectedTag::getTags).collect(Collectors.toList());
    }

    @Override
    public void deleteTags(List<String> tags, Long connectionId) throws RuntimeException {
        try {
            List<SelectedTag> tagsToDelete = selectedTagRepository.findByConnectionId(connectionId).stream()
                    .filter(tag -> tags.contains(tag.getTags()))
                    .collect(Collectors.toList());
            selectedTagRepository.deleteAll(tagsToDelete);
        } catch (Exception e) {
            throw new RuntimeException("Failed to delete tags from the database", e);
        }
    }

    @Override
    public List<String> getSavedTagsByName(String connectionName) throws TagNotFoundException {
        List<SelectedTag> savedTagsByName = selectedTagRepository.findByConnectionName(connectionName);    
    
    if(savedTagsByName.isEmpty()){
        throw new TagNotFoundException("No saved tags found for the connection");
    }
    return savedTagsByName.stream().map(SelectedTag::getTags).collect(Collectors.toList());
    }

    @Override
    public String getIpAddressByConnectionName(String connectionName) {
        // Retrieve the IP address from the connection repository based on connection name
        Connection connection = connectionRepository.findByName(connectionName);
        return connection != null ? connection.getIpAddress() : null;
    }
}
