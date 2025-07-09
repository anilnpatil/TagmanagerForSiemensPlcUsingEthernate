package com.nextfirsttag.controllers;

import com.nextfirsttag.dto.IntervalTagRequest;
import com.nextfirsttag.services.IntervalTagService;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/interval-tags")
@CrossOrigin("*")
public class IntervalTagController {

    private final IntervalTagService intervalTagService;

    public IntervalTagController(IntervalTagService intervalTagService) {
        this.intervalTagService = intervalTagService;
    }

    // Save selected tags for a given connection and interval
    @PostMapping("/save")
@CrossOrigin("*")
public ResponseEntity<Map<String, String>> saveTagsForInterval(@RequestBody IntervalTagRequest request) {
    intervalTagService.saveTagsForInterval(
        request.getConnectionId(),
        request.getInterval(),
        request.getTags()
    );
    Map<String, String> response =new HashMap<>();
    response.put("message","Tags saved successfully for interval " + request.getInterval() + "s.");
    return ResponseEntity.ok(response);
}

    // Get tags by connection and interval
    @GetMapping("/get")
    @CrossOrigin("*")
    public ResponseEntity<List<String>> getTagsForInterval(
            @RequestParam Long connectionId,
            @RequestParam int interval) {

        List<String> tags = intervalTagService.getTagsForInterval(connectionId, interval);
        return ResponseEntity.ok(tags);
    }
    
    // ✅ Delete specific tags for connection and interval (with request body)
    @DeleteMapping("/delete-specific")
    @CrossOrigin("*")
    public ResponseEntity<Map<String, String>> deleteSpecificTagsForInterval(@RequestParam Long connectionId,
            @RequestParam int interval,
            @RequestBody Map<String, List<String>> request) {
        List<String> tags = request.get("tags");
        try {
            intervalTagService.deleteSpecificTagsForInterval(connectionId, interval, tags);
            return ResponseEntity.ok(Map.of("message", "IntervalTag deselected successfully"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("error", "Failed to deselected IntervalTags"));
        }
    }

    // ✅ Delete specific tags for connection and interval (with request body)
    // @DeleteMapping("/delete-specific")
    // @CrossOrigin("*")
    // public ResponseEntity<String> deleteSpecificTagsForInterval(
    //         @RequestParam Long connectionId,
    //         @RequestParam int interval,
    //         @RequestBody Map<String, List<String>> request) {

    //     List<String> tags = request.get("tags");
    //     intervalTagService.deleteSpecificTagsForInterval(connectionId, interval, tags);
    //     return ResponseEntity.ok("Specific tags deleted for interval " + interval + "s.");
    // }

    // 🔁 Delete all tags for connection and interval (no request body)
    @DeleteMapping("/delete-all")
    @CrossOrigin("*")
    public ResponseEntity<String> deleteAllTagsForInterval(
            @RequestParam Long connectionId,
            @RequestParam int interval) {

        intervalTagService.deleteAllTagsForInterval(connectionId, interval);
        return ResponseEntity.ok("All tags deleted for interval " + interval + "s.");
    }
}
