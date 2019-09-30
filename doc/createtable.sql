CREATE TABLE public.YOUR_TABLE_NAME
(
    id varchar COLLATE pg_catalog
    .default NOT NULL,
  biz_type varchar COLLATE pg_catalog.default,
  name varchar COLLATE pg_catalog.default,
  type varchar COLLATE pg_catalog.default,
  address varchar COLLATE pg_catalog.default,
  tel varchar COLLATE pg_catalog.default,
  location varchar COLLATE pg_catalog.default,
  pcode varchar COLLATE pg_catalog.default,
  pname varchar COLLATE pg_catalog.default,
  citycode varchar COLLATE pg_catalog.default,
  cityname varchar COLLATE pg_catalog.default,
  adcode varchar COLLATE pg_catalog.default,
  adname varchar COLLATE pg_catalog.default,
  business_area varchar COLLATE pg_catalog.default,
  PRIMARY KEY
    (id)
);

ALTER TABLE public.YOUR_TABLE_NAME 
OWNER TO postgres;