package com.nextfirsttag.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Data
public class TagValueRequest {
    private Long connectionId;
    private List<TagData> tagValues;
    private LocalDateTime timestamp;
}
