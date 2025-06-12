package com.nextfirsttag.repositories;

import com.nextfirsttag.entities.Tags;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TagsRepository extends JpaRepository<Tags, Long> {
    List<Tags> findByConnectionId(Long connectionId);
}
