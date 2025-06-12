// package com.nextfirsttag.entities;

// import jakarta.persistence.Column;
// import jakarta.persistence.Entity;
// import jakarta.persistence.GeneratedValue;
// import jakarta.persistence.GenerationType;
// import jakarta.persistence.Id;
// import lombok.AllArgsConstructor;
// import lombok.Data;
// import lombok.Getter;
// import lombok.NoArgsConstructor;
// import lombok.Setter;
// @Data
// @Getter
// @Setter
// @AllArgsConstructor
// @NoArgsConstructor
// @Entity
// public class Connection {

//     @Id
//     @GeneratedValue(strategy = GenerationType.IDENTITY)
//     private Long id;

//     @Column(nullable = false, unique = true)
//     private String name;

//     @Column(nullable = false, unique = true)
//     private String ipAddress;

//     private String subnet;
//     private String gateway;

//     // for Getters and Setters used lomok annotations 
// }


package com.nextfirsttag.entities;

import jakarta.persistence.*;
import com.fasterxml.jackson.annotation.JsonManagedReference;

import lombok.*;

import java.util.List;

@Data
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Entity
public class Connection {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String name;

    @Column(nullable = false, unique = true)
    private String ipAddress;

    private String subnet;
    private String gateway;

    @OneToMany(mappedBy = "connection", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonManagedReference // Prevents circular reference during serialization
    private List<SelectedTag> selectedTags;

    @OneToMany(mappedBy = "connection", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Tags> tags;
}
