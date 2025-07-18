package com.nextfirsttag.dto;

import lombok.Data;
import java.util.List;

@Data
public class IntervalTagRequest {
    private Long connectionId;
    private Float interval;
    private List<String> tags;
}
