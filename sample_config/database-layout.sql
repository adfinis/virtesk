--
-- This is the main table containing configuration of thin clients
--

CREATE TABLE timed_thinclient_to_vm_mapping (
    vm character varying NOT NULL,
    thinclient character varying NOT NULL,
    resolution character varying NULL,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    id bigint NOT NULL,
    shutdown_vm boolean DEFAULT FALSE NOT NULL
);


--
-- mapping between thinclient and vm depending
-- on start time and priority
--

CREATE VIEW current_thinclient_to_vm_mapping AS
SELECT
    f.id,
    f.thinclient,
    f.vm,
    f.resolution,
    f.start_date,
    f.end_date,
    f.prio,
    f.shutdown_vm
FROM (
    SELECT
        timed_thinclient_to_vm_mapping.id,
        timed_thinclient_to_vm_mapping.thinclient,
        timed_thinclient_to_vm_mapping.vm,
        timed_thinclient_to_vm_mapping.resolution,
        timed_thinclient_to_vm_mapping.start_date,
        timed_thinclient_to_vm_mapping.end_date,
        0 AS prio,
        timed_thinclient_to_vm_mapping.shutdown_vm
    FROM
        timed_thinclient_to_vm_mapping
    WHERE (
        (timed_thinclient_to_vm_mapping.start_date IS NULL)
        AND
        (timed_thinclient_to_vm_mapping.end_date IS NULL)
    )
    UNION SELECT
        timed_thinclient_to_vm_mapping.id,
        timed_thinclient_to_vm_mapping.thinclient,
        timed_thinclient_to_vm_mapping.vm,
        timed_thinclient_to_vm_mapping.resolution,
        timed_thinclient_to_vm_mapping.start_date,
        timed_thinclient_to_vm_mapping.end_date,
        1 AS prio,
        timed_thinclient_to_vm_mapping.shutdown_vm
    FROM
        timed_thinclient_to_vm_mapping
    WHERE (
        (timed_thinclient_to_vm_mapping.start_date <= now())
        AND
        (timed_thinclient_to_vm_mapping.end_date IS NULL))
    UNION SELECT
        timed_thinclient_to_vm_mapping.id,
        timed_thinclient_to_vm_mapping.thinclient,
        timed_thinclient_to_vm_mapping.vm,
        timed_thinclient_to_vm_mapping.resolution,
        timed_thinclient_to_vm_mapping.start_date,
        timed_thinclient_to_vm_mapping.end_date,
        2 AS prio,
        timed_thinclient_to_vm_mapping.shutdown_vm
    FROM
        timed_thinclient_to_vm_mapping
    WHERE (
        (now() >= timed_thinclient_to_vm_mapping.start_date)
        AND
        (now() <= timed_thinclient_to_vm_mapping.end_date)
    )
) f
ORDER BY
    f.prio DESC,
    f.start_date,
    f.id;

--
-- add domain to thinclient dhcp hostname
--

CREATE VIEW dhcphostname_to_thinclient_auto_mapping AS
SELECT DISTINCT
    (((timed_thinclient_to_vm_mapping.thinclient)::text || '.thinclients.yourdomain.site'::text))::character varying AS dhcp_hostname,
    timed_thinclient_to_vm_mapping.thinclient
FROM
    timed_thinclient_to_vm_mapping
UNION SELECT DISTINCT
    timed_thinclient_to_vm_mapping.thinclient AS dhcp_hostname,
    timed_thinclient_to_vm_mapping.thinclient
FROM
    timed_thinclient_to_vm_mapping;

--
-- assign dhcp hostname to thinclient
--

CREATE TABLE dhcphostname_to_thinclient_mapping (
    dhcp_hostname character varying NOT NULL,
    thinclient character varying NOT NULL
);

--
-- assign systemuid to thinclient
--

CREATE TABLE systemuuid_to_thinclient_mapping (
    systemuuid character varying NOT NULL,
    thinclient character varying NOT NULL
);

--
-- view combining dhcp host, system id and thinclient
--

CREATE VIEW sysinfo_to_thinclient_mapping AS
SELECT
    f.dhcp_hostname,
    f.systemuuid,
    f.thinclient,
    f.prio
FROM (
    SELECT
        dhcphostname_to_thinclient_auto_mapping.dhcp_hostname,
        NULL::character varying AS systemuuid,
        dhcphostname_to_thinclient_auto_mapping.thinclient,
        100 AS prio
    FROM
        dhcphostname_to_thinclient_auto_mapping
    UNION SELECT
        dhcphostname_to_thinclient_mapping.dhcp_hostname,
        NULL::character varying AS systemuuid,
        dhcphostname_to_thinclient_mapping.thinclient,
        200 AS prio
    FROM
        dhcphostname_to_thinclient_mapping
    UNION SELECT
        NULL::character varying AS dhcp_hostname,
        systemuuid_to_thinclient_mapping.systemuuid,
        systemuuid_to_thinclient_mapping.thinclient,
        300 AS prio
    FROM
        systemuuid_to_thinclient_mapping
) f
ORDER BY
    f.prio DESC;

--
-- View combining all tables concerning thin client
--

CREATE VIEW thinclient_everything_view AS
SELECT DISTINCT
    s.thinclient,
    c.vm,
    c.resolution,
    s.dhcp_hostname,
    s.systemuuid,
    c.id,
    c.start_date,
    c.end_date,
    c.prio,
    c.shutdown_vm
FROM (
    sysinfo_to_thinclient_mapping s
    LEFT JOIN current_thinclient_to_vm_mapping c ON (((s.thinclient)::text = (c.thinclient)::text))
)
ORDER BY
    c.prio DESC,
    c.start_date,
    c.id;

CREATE SEQUENCE timed_thinclient_to_vm_mapping_id_seq
START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER TABLE ONLY timed_thinclient_to_vm_mapping
ALTER COLUMN id
SET DEFAULT nextval('timed_thinclient_to_vm_mapping_id_seq'::regclass);

ALTER TABLE ONLY dhcphostname_to_thinclient_mapping
ADD CONSTRAINT dhcphostname_to_thinclient_mapping_pkey PRIMARY KEY (dhcp_hostname);

ALTER TABLE ONLY systemuuid_to_thinclient_mapping
ADD CONSTRAINT systemuuid_to_thinclient_mapping_pkey PRIMARY KEY (systemuuid);

ALTER TABLE ONLY timed_thinclient_to_vm_mapping
ADD CONSTRAINT timed_thinclient_to_vm_mapping_pkey PRIMARY KEY (id);
