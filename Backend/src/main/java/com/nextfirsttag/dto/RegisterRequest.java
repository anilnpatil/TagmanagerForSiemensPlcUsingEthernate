package com.nextfirsttag.dto;

import com.nextfirsttag.entities.Role;
import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RegisterRequest {
   private String username;
    private String password;
    private Role role; // USER or ADMIN
}
  

