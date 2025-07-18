package com.nextfirsttag.entities;

import java.time.Instant;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
@Data
@AllArgsConstructor
@NoArgsConstructor
@Entity
@Table(name = "tag_value_log")
public class TagValueLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "connection_id", nullable = false)
    private Integer connectionId;

    @Column(name = "tag_name", nullable = false)
    private String tagName;

    @Column(name = "tag_value")
    private String tagValue;

    @Column(name = "interval_seconds", nullable = false, scale = 2)
    private Double intervalSeconds;

    @Column(name = "timestamp", nullable = false)
    private Instant timestamp;

    // Getters and Setters
}
