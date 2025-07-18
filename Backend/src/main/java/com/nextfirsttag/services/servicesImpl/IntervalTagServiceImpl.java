package com.nextfirsttag.services.servicesImpl;

import com.nextfirsttag.dto.IntervalTagGroupDTO;
import com.nextfirsttag.entities.Connection;
import com.nextfirsttag.entities.IntervalTag;
import com.nextfirsttag.repositories.ConnectionRepository;
import com.nextfirsttag.repositories.IntervalTagRepository;
import com.nextfirsttag.services.IntervalTagService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class IntervalTagServiceImpl implements IntervalTagService {

    private final IntervalTagRepository intervalTagRepository;
    private final ConnectionRepository connectionRepository;

    public IntervalTagServiceImpl(IntervalTagRepository intervalTagRepository, ConnectionRepository connectionRepository) {
        this.intervalTagRepository = intervalTagRepository;
        this.connectionRepository = connectionRepository;
    }

    @Transactional
    @Override
    public void saveTagsForInterval(Long connectionId, Float interval, List<String> tags) {
        Connection connection = connectionRepository.findById(connectionId)
                .orElseThrow(() -> new RuntimeException("Connection not found"));

        List<IntervalTag> intervalTags = tags.stream()
                .map(tag -> new IntervalTag(null, tag, interval, connection))
                .collect(Collectors.toList());

        intervalTagRepository.saveAll(intervalTags);
    }

    @Override
    public List<String> getTagsForInterval(Long connectionId, Float interval) {
        return intervalTagRepository.findByConnectionIdAndInterval(connectionId, interval)
                .stream()
                .map(IntervalTag::getTag)
                .collect(Collectors.toList());
    }

    @Override
    public List<IntervalTagGroupDTO> getGroupedTagsByConnection(Long connectionId) {
        List<IntervalTag> tags = intervalTagRepository.findByConnectionId(connectionId);

        return tags.stream()
                .collect(Collectors.groupingBy(IntervalTag::getInterval))
                .entrySet()
                .stream()
                .map(entry -> new IntervalTagGroupDTO(
                        entry.getKey(),
                        entry.getValue().stream().map(IntervalTag::getTag).collect(Collectors.toList())
                ))
                .sorted((a, b) -> Float.compare(a.getInterval(), b.getInterval()))
                .collect(Collectors.toList());
    }


    @Transactional
    @Override
    public void deleteSpecificTagsForInterval(Long connectionId, Float interval, List<String> tags) {
        List<IntervalTag> intervalTags = intervalTagRepository.findByConnectionIdAndInterval(connectionId, interval)
                .stream()
                .filter(it -> tags.contains(it.getTag()))
                .collect(Collectors.toList());

        intervalTagRepository.deleteAll(intervalTags);
    }

    @Transactional
    @Override
    public void deleteAllTagsForInterval(Long connectionId, Float interval) {
        List<IntervalTag> intervalTags = intervalTagRepository.findByConnectionIdAndInterval(connectionId, interval);
        intervalTagRepository.deleteAll(intervalTags);
    }
}
