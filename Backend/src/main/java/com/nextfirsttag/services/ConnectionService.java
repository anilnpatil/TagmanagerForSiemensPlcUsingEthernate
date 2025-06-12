package com.nextfirsttag.services;

import java.util.List;
import java.util.Optional;

import com.nextfirsttag.entities.Connection;

public interface ConnectionService {
      
    public List<Connection> getAllConnections() ;
    public Connection saveConnection(Connection connection) ;

    public Optional<Connection> getConnectionById(Long id) ;

    public void deleteConnection(Long id);
}

