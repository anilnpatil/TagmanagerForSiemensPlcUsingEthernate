package com.nextfirsttag.services;

import com.nextfirsttag.entities.User;

import java.util.List;

public interface UserService {
    List<User> getAllUsers();
    boolean deleteUser(Long id);
}
