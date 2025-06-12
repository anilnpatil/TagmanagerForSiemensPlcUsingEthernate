package com.nextfirsttag.repositories;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.transaction.annotation.Transactional;

import com.nextfirsttag.entities.Connection;
import com.nextfirsttag.entities.SelectedTag;

public interface SelectedTagRepository extends JpaRepository<SelectedTag, Long>{
  @Transactional
    void deleteByTagsIn(List<String> tags);

  List<String> findByConnection(Connection connection);

  List<SelectedTag> findByConnectionId(Long connectionId);
  List<SelectedTag> findByConnectionName(String connectionName);
}
