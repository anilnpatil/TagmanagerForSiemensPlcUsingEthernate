package com.nextfirsttag.entities;

import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.JoinColumn;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.Getter;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Setter
@Getter
@Entity
public class SelectedTag {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long tagId;

    private String tags;

    @ManyToOne
    @JoinColumn(name = "connection_id", nullable = false)
    @JsonBackReference // Prevents circular reference during serialization
    private Connection connection;
}
