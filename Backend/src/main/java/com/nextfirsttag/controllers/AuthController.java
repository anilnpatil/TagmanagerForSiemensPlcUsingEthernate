package com.nextfirsttag.controllers;

import com.nextfirsttag.dto.ApiResponse;
import com.nextfirsttag.dto.AuthRequest;
import com.nextfirsttag.dto.RegisterRequest;
import com.nextfirsttag.entities.User;
import com.nextfirsttag.repositories.UserRepository;
import com.nextfirsttag.security.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.*;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/auth")
@CrossOrigin("*")
public class AuthController {

    @Autowired
    private UserRepository userRepo;

    @Autowired
    private PasswordEncoder encoder;

    @Autowired
    private AuthenticationManager authManager;

    @Autowired
    private JwtUtil jwtUtil; 
    
    @PostMapping("/register")
    public ResponseEntity<ApiResponse> register(@RequestBody RegisterRequest req) {
        try {
            User user = User.builder()
                    .username(req.getUsername())
                    .password(encoder.encode(req.getPassword()))
                    .role(req.getRole())
                    .build();

            userRepo.save(user);

            return ResponseEntity.ok(new ApiResponse("success", "User registered successfully"));
        } catch (Exception e) {
            return ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(new ApiResponse("error", "Registration failed: " + e.getMessage()));
        }
    }

@PostMapping("/login")
public Map<String, String> login(@RequestBody AuthRequest req) {
    authManager.authenticate(
        new UsernamePasswordAuthenticationToken(req.getUsername(), req.getPassword())
    );

    User user = userRepo.findByUsername(req.getUsername())
            .orElseThrow(() -> new UsernameNotFoundException("User not found"));

    String token = jwtUtil.generateToken(user.getUsername(), user.getRole().name());

    return Map.of("token", token);
}

}
