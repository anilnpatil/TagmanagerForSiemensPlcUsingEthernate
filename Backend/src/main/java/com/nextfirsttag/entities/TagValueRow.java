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

    // Fixed tag fields
    private Double DB4_DBD0;
    private Double DB4_DBD4;
    private Double DB4_DBD8;
    private Double DB4_DBD12;
    private Double DB4_DBD16;
    private Double DB4_DBD20;
    private Double DB4_DBD24;
    private Double DB4_DBD28;
    private Double DB4_DBD32;
    private Double DB4_DBD36;
    private Double DB4_DBD40;
    private Double DB4_DBD44;
    private Double DB4_DBD48;
    private Double DB4_DBD52;
    private Double DB4_DBD56;
    private Double DB4_DBD60;
    private Double DB4_DBD64;
    private Double DB4_DBD68;
    private Double DB4_DBD72;

    private Double DB5_DBD0;
    private Double DB5_DBD4;
    private Double DB5_DBD8;
    private Double DB5_DBD12;
    private Double DB5_DBD16;
    private Double DB5_DBD20;
    private Double DB5_DBD24;
    private Double DB5_DBD28;
    private Double DB5_DBD32;
    private Double DB5_DBD36;
    private Double DB5_DBD40;
    private Double DB5_DBD44;
    private Double DB5_DBD48;
    private Double DB5_DBD52;
    private Double DB5_DBD56;
    private Double DB5_DBD60;
    private Double DB5_DBD64;
    private Double DB5_DBD68;
    private Double DB5_DBD72;

    private String DB6_DBX0;
    private String DB6_DBX256;
    private String DB6_DBX512;
    private String DB6_DBX768;



    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "connection_id")
    private Connection connection;
}
