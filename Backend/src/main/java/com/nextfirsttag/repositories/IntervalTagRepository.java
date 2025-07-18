package com.nextfirsttag.repositories;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import com.nextfirsttag.entities.IntervalTag;

public interface IntervalTagRepository extends JpaRepository<IntervalTag, Long> {
    List<IntervalTag> findByConnectionIdAndInterval(Long connectionId, Float interval);
    List<IntervalTag> findByConnectionId(Long connectionId);
    void deleteByConnectionIdAndInterval(Long connectionId, Float interval);
}
