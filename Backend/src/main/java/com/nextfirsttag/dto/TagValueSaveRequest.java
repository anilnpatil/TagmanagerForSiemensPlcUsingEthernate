package com.nextfirsttag.dto;

import java.time.Instant;
import java.util.List;

import lombok.Data;

@Data
public class TagValueSaveRequest {
    private Integer connectionId;
    private Instant timestamp;
    private List<IntervalTagGroup> intervalTagValues;
}

