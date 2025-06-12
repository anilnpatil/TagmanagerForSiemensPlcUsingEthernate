package com.nextfirsttag.services.servicesImpl;

import com.nextfirsttag.dto.TagData;
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

        for (TagData tagData : request.getTagValues()) {
            switch (tagData.getTag()) {
                case "DB1_DBD0": row.setDB1_DBD0(tagData.getValue()); break;
                case "DB1_DBD4": row.setDB1_DBD4(tagData.getValue()); break;
                case "DB1_DBD8": row.setDB1_DBD8(tagData.getValue()); break;
                case "DB1_DBD12": row.setDB1_DBD12(tagData.getValue()); break;
                case "DB1_DBD16": row.setDB1_DBD16(tagData.getValue()); break;
                case "DB1_DBD20": row.setDB1_DBD20(tagData.getValue()); break;
                case "DB1_DBD24": row.setDB1_DBD24(tagData.getValue()); break;
                case "DB1_DBD28": row.setDB1_DBD28(tagData.getValue()); break;
                case "DB1_DBD32": row.setDB1_DBD32(tagData.getValue()); break;
                case "DB1_DBD36": row.setDB1_DBD36(tagData.getValue()); break;
                case "DB1_DBD40": row.setDB1_DBD40(tagData.getValue()); break;
                case "DB1_DBD44": row.setDB1_DBD44(tagData.getValue()); break;
                case "DB1_DBD48": row.setDB1_DBD48(tagData.getValue()); break;
                case "DB1_DBD52": row.setDB1_DBD52(tagData.getValue()); break;
                case "DB1_DBD56": row.setDB1_DBD56(tagData.getValue()); break;
                case "DB1_DBD60": row.setDB1_DBD60(tagData.getValue()); break;
                case "DB1_DBD64": row.setDB1_DBD64(tagData.getValue()); break;
                case "DB1_DBD68": row.setDB1_DBD68(tagData.getValue()); break;
                case "DB1_DBD72": row.setDB1_DBD72(tagData.getValue()); break;
                case "DB1_DBD76": row.setDB1_DBD76(tagData.getValue()); break;
                case "DB1_DBD80": row.setDB1_DBD80(tagData.getValue()); break;
                case "DB1_DBD84": row.setDB1_DBD84(tagData.getValue()); break;
                case "DB1_DBD88": row.setDB1_DBD88(tagData.getValue()); break;
                case "DB1_DBD92": row.setDB1_DBD92(tagData.getValue()); break;
                case "DB1_DBD96": row.setDB1_DBD96(tagData.getValue()); break;
                case "DB1_DBD100": row.setDB1_DBD100(tagData.getValue()); break; 
                case "DB1_DBD104": row.setDB1_DBD104(tagData.getValue()); break;
            }
        }

        row.setConnection(connection);
        rowRepo.save(row);
    }
   
    @Override
public Page<TagValueResponse> getTagValuesByConnection(Long connectionId, Pageable pageable) {
    Page<TagValueRow> rows = rowRepo.findByConnectionId(connectionId, pageable);

    return rows.map(row -> {
        TagValueResponse dto = new TagValueResponse();
        dto.setDB1_DBD0(row.getDB1_DBD0());
        dto.setDB1_DBD4(row.getDB1_DBD4());
        dto.setDB1_DBD8(row.getDB1_DBD8());
        dto.setDB1_DBD12(row.getDB1_DBD12());
        dto.setDB1_DBD16(row.getDB1_DBD16());
        dto.setDB1_DBD20(row.getDB1_DBD20());
        dto.setDB1_DBD24(row.getDB1_DBD24());
        dto.setDB1_DBD28(row.getDB1_DBD28());
        dto.setDB1_DBD32(row.getDB1_DBD32());
        dto.setDB1_DBD36(row.getDB1_DBD36());
        dto.setDB1_DBD40(row.getDB1_DBD40());
        dto.setDB1_DBD44(row.getDB1_DBD44());
        dto.setDB1_DBD48(row.getDB1_DBD48());
        dto.setDB1_DBD52(row.getDB1_DBD52());
        dto.setDB1_DBD56(row.getDB1_DBD56());
        dto.setDB1_DBD60(row.getDB1_DBD60());
        dto.setDB1_DBD64(row.getDB1_DBD64());
        dto.setDB1_DBD68(row.getDB1_DBD68());
        dto.setDB1_DBD72(row.getDB1_DBD72());
        dto.setDB1_DBD76(row.getDB1_DBD76());
        dto.setDB1_DBD80(row.getDB1_DBD80());
        dto.setDB1_DBD84(row.getDB1_DBD84());
        dto.setDB1_DBD88(row.getDB1_DBD88());
        dto.setDB1_DBD92(row.getDB1_DBD92());
        dto.setDB1_DBD96(row.getDB1_DBD96());
        dto.setDB1_DBD100(row.getDB1_DBD100());
        // Set other DB1_DBD* values here
        dto.setTimestamp(row.getTimestamp());
        dto.setConnectionId(row.getConnection().getId());
        return dto;
    });
}
}
