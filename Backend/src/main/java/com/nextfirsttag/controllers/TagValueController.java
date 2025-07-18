package com.nextfirsttag.controllers;

import com.nextfirsttag.dto.TagValueRequest;
import com.nextfirsttag.services.TagValueService;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@CrossOrigin("*")
@RequestMapping("/tagValues")
public class TagValueController {
  
 private TagValueService tagValueService;

 public TagValueController (TagValueService tagValueService)  {
   this.tagValueService =  tagValueService;
 }

@PostMapping("/save")
public ResponseEntity<Map<String, String>> saveTagValues(@RequestBody TagValueRequest request) {
    tagValueService.saveTagValues(request);
    Map<String, String> response = new HashMap<>();
    response.put("status", "success");
    response.put("message", "Tag values saved successfully");
    return ResponseEntity.ok(response);
}

    @GetMapping("/byConnection")
    public ResponseEntity<?> getByConnection(@RequestParam Long connectionId,
                                             @RequestParam(defaultValue = "0") int page,
                                             @RequestParam(defaultValue = "15") int size) {
        return ResponseEntity.ok(tagValueService.getTagValuesByConnection(connectionId, PageRequest.of(page, size)));
    }
}