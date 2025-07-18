// dto/IntervalTagGroupDTO.java
package com.nextfirsttag.dto;

import java.util.List;

public class IntervalTagGroupDTO {
    private Float interval;
    private List<String> tags;

    public IntervalTagGroupDTO(Float interval, List<String> tags) {
        this.interval = interval;
        this.tags = tags;
    }

    public Float getInterval() {
        return interval;
    }

    public void setInterval(Float interval) {
        this.interval = interval;
    }

    public List<String> getTags() {
        return tags;
    }

    public void setTags(List<String> tags) {
        this.tags = tags;
    }
}

