package com.nextfirsttag.entities;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Data
@AllArgsConstructor
@NoArgsConstructor
public class TagValueRow {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private LocalDateTime timestamp;

    private Double DB1_DBD0;
    private Double DB1_DBD4;
    private Double DB1_DBD8;
    private Double DB1_DBD12;
    private Double DB1_DBD16;
    private Double DB1_DBD20;
    private Double DB1_DBD24;
    private Double DB1_DBD28;
    private Double DB1_DBD32;
    private Double DB1_DBD36;
    private Double DB1_DBD40;
    private Double DB1_DBD44;
    private Double DB1_DBD48;
    private Double DB1_DBD52;
    private Double DB1_DBD56;
    private Double DB1_DBD60;
    private Double DB1_DBD64;
    private Double DB1_DBD68;
    private Double DB1_DBD72;
    private Double DB1_DBD76;
    private Double DB1_DBD80;
    private Double DB1_DBD84;
    private Double DB1_DBD88;
    private Double DB1_DBD92;
    private Double DB1_DBD96;
    private Double DB1_DBD100;
    private Double DB1_DBD104;


    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "connection_id")
    private Connection connection;
}
