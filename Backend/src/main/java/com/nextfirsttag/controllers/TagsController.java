package com.nextfirsttag.controllers;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;


import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import com.nextfirsttag.entities.SelectedTag;
import com.nextfirsttag.services.TagsService;

@RestController
@CrossOrigin("*")
public class TagsController {

    private static final String PYTHON_API_BASE_URL = "http://localhost:8083/getTagValues";

    private final TagsService tagsService;

    public TagsController(TagsService tagService) {
        this.tagsService = tagService;
    }
    ///this method not used if want to use need changes
    @GetMapping("/listTags")
    public ResponseEntity<Map<String, List<String>>> listTags() {
        Map<String, List<String>> tags = tagsService.getAllTags();
        return ResponseEntity.ok(tags);
    }

    @PostMapping("/saveSelectedTags")
    public ResponseEntity<Map<String, Object>> saveSelectedTags(@RequestBody Map<String, Object> request) {
        List<String> selectedTags = (List<String>) request.get("tags");
        Long connectionId = ((Number) request.get("connectionId")).longValue();
        tagsService.saveSelectedTags(selectedTags, connectionId);
        List<SelectedTag> savedTags = tagsService.getSavedTags();
        List<String> tagNames = savedTags.stream().map(SelectedTag::getTags).collect(Collectors.toList());
        return ResponseEntity.ok(Map.of("message", "Selected tags shifted to database successfully", "savedTags", tagNames));
    }

    @GetMapping("/getSavedTagsById")
    public ResponseEntity<List<String>> getSavedTags(@RequestParam Long connectionId) {
        List<String> tagNames = tagsService.getSavedTags(connectionId);
        return ResponseEntity.ok(tagNames);
    }

    @DeleteMapping("/deleteTags")
    public ResponseEntity<Map<String, String>> deleteTags(@RequestBody Map<String, List<String>> request, @RequestParam Long connectionId) {
        List<String> tags = request.get("tags");
        try {
            tagsService.deleteTags(tags, connectionId);
            return ResponseEntity.ok(Map.of("message", "Tag deselected successfully"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("error", "Failed to delete tags"));
        }
    }
    @GetMapping("/getSavedTagsByName")
    public ResponseEntity<List<String>> getSavedTagsByName(@RequestParam String connectionName) {
        List<String> tagNames = tagsService.getSavedTagsByName(connectionName);
        return ResponseEntity.ok(tagNames);
    }

     @GetMapping("/getSavedTagValuesByName")
    public ResponseEntity<List<Map<String, Object>>> findSavedTagsByName(@RequestParam String connectionName) {
        // Fetch the tags and IP address based on the connection name
        List<String> tagNames = tagsService.getSavedTagsByName(connectionName);
        String ipAddress = tagsService.getIpAddressByConnectionName(connectionName);

        if (ipAddress == null) {
            return ResponseEntity.badRequest().body(null);
        }

        // Call the Python service with the tags and IP address
        List<Map<String, Object>> tagValues = fetchTagValuesFromPython(ipAddress, tagNames);

        return ResponseEntity.ok(tagValues);
    }

    private List<Map<String, Object>> fetchTagValuesFromPython(String ipAddress, List<String> tagNames) {
        RestTemplate restTemplate = new RestTemplate();
        HttpHeaders headers = new HttpHeaders();
        headers.set("Content-Type", "application/json");

        // Create the payload in the required format
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("tags", tagNames);

        HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestBody, headers);

        // Construct the URL with the IP address
        String url = PYTHON_API_BASE_URL + "?ip=" + ipAddress;

        ResponseEntity<List> responseEntity = restTemplate.exchange(
                url,
                HttpMethod.POST,
                requestEntity,
                List.class
        );

        return responseEntity.getBody();
    }
}

