package com.nextfirsttag.dto;

import lombok.Data;
import java.util.List;

@Data
public class IntervalTagRequest {
    private Long connectionId;
    private int interval;
    private List<String> tags;
}
