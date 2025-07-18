package com.nextfirsttag.repositories;

import org.springframework.data.jpa.repository.JpaRepository;

import com.nextfirsttag.entities.TagValueLog;

public interface TagValueLogRepository extends JpaRepository<TagValueLog, Long> {
}
