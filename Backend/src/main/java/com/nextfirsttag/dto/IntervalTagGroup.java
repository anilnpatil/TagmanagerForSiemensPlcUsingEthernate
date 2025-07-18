package com.nextfirsttag.dto;

import java.util.List;

import lombok.Data;

@Data
 public class IntervalTagGroup {
    private Double interval;
    private List<TagValueEntry> tags;
}
