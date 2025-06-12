package com.nextfirsttag.entities;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
@Data
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@Entity
public class Tags {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "tagId") // Maps the field to the database column
    private Long tagId;

    private String tag;

    @ManyToOne
    @JoinColumn(name = "connection_id") // Explicitly map the foreign key
    private Connection connection;
}