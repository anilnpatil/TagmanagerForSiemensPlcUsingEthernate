// package com.nextfirsttag.services.servicesImpl;


// import com.nextfirsttag.entities.Connection;
// import com.nextfirsttag.repositories.ConnectionRepository;
// import com.nextfirsttag.services.ConnectionService;

// import org.springframework.beans.factory.annotation.Autowired;
// import org.springframework.stereotype.Service;

// import java.util.List;
// import java.util.Optional;

// @Service
// public class ConnectionServiceImpl implements ConnectionService{

//     @Autowired
//     private ConnectionRepository connectionRepository;
//     @Override
//     public List<Connection> getAllConnections() {
//         return connectionRepository.findAll();
//     }
//     @Override
//     public Connection saveConnection(Connection connection) {
//         return connectionRepository.save(connection);
//     }
//     @Override
//     public Optional<Connection> getConnectionById(Long id) {
//         return connectionRepository.findById(id);
//     }
//     @Override
//     public void deleteConnection(Long id) {
//         connectionRepository.deleteById(id);
//     }
// }

package com.nextfirsttag.services.servicesImpl;

import com.nextfirsttag.entities.Connection;
import com.nextfirsttag.repositories.ConnectionRepository;
import com.nextfirsttag.services.ConnectionService;

import jakarta.persistence.EntityNotFoundException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class ConnectionServiceImpl implements ConnectionService {

    @Autowired
    private ConnectionRepository connectionRepository;

    @Override
    public List<Connection> getAllConnections() {
        return connectionRepository.findAll();
    }

    @Override
    public Connection saveConnection(Connection connection) {
        // Check for duplicate name
        if (connectionRepository.findByName(connection.getName()) != null) {
            throw new IllegalArgumentException("Duplicate name: " + connection.getName());
        }

        // Check for duplicate IP address
        Optional<Connection> existingConnection = connectionRepository.findAll().stream()
                .filter(conn -> conn.getIpAddress().equals(connection.getIpAddress()))
                .findFirst();

        if (existingConnection.isPresent()) {
            throw new IllegalArgumentException("Duplicate IP Address: " + connection.getIpAddress());
        }

        return connectionRepository.save(connection);
    }

    @Override
    public Optional<Connection> getConnectionById(Long id) {
        return connectionRepository.findById(id);
    }

    // @Override
    // public void deleteConnection(Long id) {
    //     connectionRepository.deleteById(id);
    // }

    @Override
public void deleteConnection(Long id) {
    if (connectionRepository.existsById(id)) {
        connectionRepository.deleteById(id);
    } else {
        throw new EntityNotFoundException("Connection with ID " + id + " not found");
    }
}

}
