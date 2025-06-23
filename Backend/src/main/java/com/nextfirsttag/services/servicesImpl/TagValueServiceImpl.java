package com.nextfirsttag.services.servicesImpl;

import com.nextfirsttag.dto.TagValueRequest;
import com.nextfirsttag.dto.TagValueResponse;
import com.nextfirsttag.entities.Connection;
import com.nextfirsttag.entities.TagValueRow;
import com.nextfirsttag.repositories.ConnectionRepository;
import com.nextfirsttag.repositories.TagValueRowRepository;
import com.nextfirsttag.services.TagValueService;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.Map;

@Service
public class TagValueServiceImpl implements TagValueService {

    private final TagValueRowRepository rowRepo;
    private final ConnectionRepository connectionRepo;

    public TagValueServiceImpl(TagValueRowRepository rowRepo, ConnectionRepository connectionRepo) {
        this.rowRepo = rowRepo;
        this.connectionRepo = connectionRepo;
    }

    @Override
    public void saveTagValues(TagValueRequest request) {
        TagValueRow row = new TagValueRow();
        row.setTimestamp(request.getTimestamp());

        Connection connection = connectionRepo.findById(request.getConnectionId())
                .orElseThrow(() -> new RuntimeException("Connection not found"));
        row.setConnection(connection);

        Map<String, Object> tagMap = request.getTagValues();

        for (Map.Entry<String, Object> entry : tagMap.entrySet()) {
            String fieldName = entry.getKey();
            Object value = entry.getValue();

            try {
                Field field = TagValueRow.class.getDeclaredField(fieldName);
                field.setAccessible(true);

                Class<?> type = field.getType();
                if (value != null) {
                    Object castedValue = convertType(value, type);
                    field.set(row, castedValue);
                }

            } catch (NoSuchFieldException | IllegalAccessException e) {
                System.out.println("Field not found or cannot be set: " + fieldName);
            }
        }

        rowRepo.save(row);
    }

    private Object convertType(Object value, Class<?> targetType) {
        if (targetType == Double.class || targetType == double.class) return Double.valueOf(value.toString());
        if (targetType == Integer.class || targetType == int.class) return Integer.valueOf(value.toString());
        if (targetType == Boolean.class || targetType == boolean.class) return Boolean.valueOf(value.toString());
        if (targetType == Float.class || targetType == float.class) return Float.valueOf(value.toString());
        if (targetType == String.class) return value.toString();
        return null;
    }

    @Override
    public Page<TagValueResponse> getTagValuesByConnection(Long connectionId, Pageable pageable) {
        Page<TagValueRow> rows = rowRepo.findByConnectionId(connectionId, pageable);

        return rows.map(row -> {
            TagValueResponse dto = new TagValueResponse();
            dto.setConnectionId(row.getConnection().getId());
            dto.setTimestamp(row.getTimestamp());

            Field[] fields = TagValueRow.class.getDeclaredFields();
            for (Field field : fields) {
                if (!Modifier.isStatic(field.getModifiers())
                        && !field.getName().equals("id")
                        && !field.getName().equals("timestamp")
                        && !field.getName().equals("connection")) {
                    field.setAccessible(true);
                    try {
                        Object value = field.get(row);
                        dto.getTagValues().put(field.getName(), value);
                    } catch (IllegalAccessException ignored) {}
                }
            }

            return dto;
        });
    }
}
