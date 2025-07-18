package com.nextfirsttag.controllers;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.nextfirsttag.dto.ApiResponse;
import com.nextfirsttag.dto.TagValueSaveRequest;
import com.nextfirsttag.services.TagValueLogService;

@RestController
@RequestMapping("/tagValues")
@CrossOrigin("*")
public class TagValueLogController {

    @Autowired
    private final TagValueLogService tagValueLogService;

    public TagValueLogController(TagValueLogService tagValueLogService) {
        this.tagValueLogService = tagValueLogService;
    }

    @PostMapping("/saveBatch")
    public ResponseEntity<ApiResponse> saveTagValues(@RequestBody TagValueSaveRequest request) {
        try {
            tagValueLogService.saveAll(request);
            return ResponseEntity.ok(new ApiResponse("success", "Tag values saved successfully"));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(new ApiResponse("error", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(new ApiResponse("error", "Internal server error while saving tag values"));
        }
    }
}

