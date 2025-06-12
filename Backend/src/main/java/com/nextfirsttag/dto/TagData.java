package com.nextfirsttag.dto;

import lombok.*;

import java.time.LocalDateTime;

@Data
public class TagData {
    private String tag;
    private Double value;
    private LocalDateTime timestamp;
}

