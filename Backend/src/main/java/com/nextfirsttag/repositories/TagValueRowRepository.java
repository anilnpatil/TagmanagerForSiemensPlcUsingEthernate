package com.nextfirsttag.repositories;

import com.nextfirsttag.entities.TagValueRow;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TagValueRowRepository extends JpaRepository<TagValueRow, Long> {
    Page<TagValueRow> findByConnectionId(Long connectionId, Pageable pageable);
}
