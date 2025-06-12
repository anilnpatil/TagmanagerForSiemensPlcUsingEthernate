package com.nextfirsttag.services;

import com.nextfirsttag.dto.AuthRequest;
import com.nextfirsttag.dto.AuthResponse;
import com.nextfirsttag.dto.RegisterRequest;
import com.nextfirsttag.entities.Role;
import com.nextfirsttag.entities.User;
import com.nextfirsttag.repositories.UserRepository;
import com.nextfirsttag.security.JwtUtil;
import lombok.RequiredArgsConstructor;

import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final AuthenticationManager authenticationManager;

    public AuthResponse register(RegisterRequest request) {
        // Create user object
        User user = new User();
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setRole(request.getRole() != null ? request.getRole() : Role.USER); // Default to USER

        // Save user in DB
        userRepository.save(user);

        // Generate JWT token
        String token = jwtUtil.generateToken(user);

        return new AuthResponse(token);
    }

    public AuthResponse authenticate(AuthRequest request) {
        try {
            authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                    request.getUsername(),
                    request.getPassword()
                )
            );
        } catch (AuthenticationException ex) {
            throw new RuntimeException("Invalid username or password");
        }

        // Fetch user from DB
        Optional<User> userOptional = userRepository.findByUsername(request.getUsername());
        if (userOptional.isEmpty()) {
            throw new RuntimeException("User not found");
        }

        User user = userOptional.get();
        // Generate JWT token
        String token = jwtUtil.generateToken(user);

        return new AuthResponse(token);
    }
}
