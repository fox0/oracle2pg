CREATE TABLE ss_cls (
    id          NUMBER NOT NULL,
    cls         VARCHAR2(100 CHAR) NOT NULL,
    query       VARCHAR2(200 CHAR) NOT NULL,
    table_name  VARCHAR2(30 CHAR) NOT NULL
);
ALTER TABLE ss_cls ADD CONSTRAINT ss_cls_pk PRIMARY KEY ( id );

CREATE TABLE supplier
( supplier_id numeric(10) not null,
  supplier_name varchar2(50) not null,
  contact_name varchar2(50)
);
ALTER TABLE supplier ADD CONSTRAINT supplier_pk PRIMARY KEY (supplier_id );

CREATE TABLE products
( product_id numeric(10) not null,
  supplier_id numeric(10) not null
);
ALTER TABLE products
ADD CONSTRAINT fk_supplier
  FOREIGN KEY (supplier_id)
  REFERENCES supplier(supplier_id);
