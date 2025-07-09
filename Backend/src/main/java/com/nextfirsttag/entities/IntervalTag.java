package com.nextfirsttag.entities;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Data
@AllArgsConstructor
@NoArgsConstructor
public class IntervalTag {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private int interval; // e.g., 1, 2, 3...

    private String tag;

    @ManyToOne
    @JoinColumn(name = "connection_id", nullable = false)
    private Connection connection;

     // ADD THIS CONSTRUCTOR IF USING LOMBOK DOESN'T COVER IT
    public IntervalTag(Long id, String tag, int interval, Connection connection) {
        this.id = id;
        this.tag = tag;
        this.interval = interval;
        this.connection = connection;
    }
}