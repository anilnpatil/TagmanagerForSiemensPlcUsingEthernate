package com.nextfirsttag.dto;

import lombok.*;

import java.time.LocalDateTime;
// import java.util.List;
import java.util.Map;

@Data
public class TagValueRequest {
    private Long connectionId;
    // private List<TagData> tagValues;
    private LocalDateTime timestamp;
    private Map<String, Object> tagValues;
}
