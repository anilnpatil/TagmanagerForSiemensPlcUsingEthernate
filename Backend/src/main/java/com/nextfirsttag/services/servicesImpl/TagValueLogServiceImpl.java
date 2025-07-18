package com.nextfirsttag.services.servicesImpl;

import jakarta.transaction.Transactional;
import org.springframework.stereotype.Service;

import com.nextfirsttag.dto.IntervalTagGroup;
import com.nextfirsttag.dto.TagValueEntry;
import com.nextfirsttag.dto.TagValueSaveRequest;
import com.nextfirsttag.entities.TagValueLog;
import com.nextfirsttag.repositories.TagValueLogRepository;
import com.nextfirsttag.services.TagValueLogService;


import java.util.ArrayList;
import java.util.List;

@Service
public class TagValueLogServiceImpl implements TagValueLogService {

    private final TagValueLogRepository repository;

    public TagValueLogServiceImpl(TagValueLogRepository repository) {
        this.repository = repository;
    }

    @Override
    @Transactional
    public void saveAll(TagValueSaveRequest request) {
        if (request.getIntervalTagValues() == null || request.getIntervalTagValues().isEmpty()) {
            throw new IllegalArgumentException("No interval tag values provided.");
        }

        List<TagValueLog> logs = new ArrayList<>();

        for (IntervalTagGroup group : request.getIntervalTagValues()) {
            if (group.getTags() == null || group.getTags().isEmpty()) continue;

            for (TagValueEntry tag : group.getTags()) {
                if (tag.getName() == null || tag.getName().isEmpty()) continue;

                TagValueLog log = new TagValueLog();
                log.setConnectionId(request.getConnectionId());
                log.setTagName(tag.getName());
                log.setTagValue(tag.getValue() != null ? tag.getValue().toString() : null);
                log.setIntervalSeconds(group.getInterval() != null ? group.getInterval() : 0.0);
                log.setTimestamp(request.getTimestamp());

                logs.add(log);
            }
        }

        if (!logs.isEmpty()) {
            repository.saveAll(logs);
        } else {
            throw new IllegalArgumentException("No valid tags to save.");
        }
    }
}
