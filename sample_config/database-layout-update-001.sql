--
-- Update database layout from previous version
--

ALTER TABLE timed_thinclient_to_vm_mapping ADD resolution character varying NULL;

DROP VIEW current_thinclient_to_vm_mapping;
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


ALTER TABLE public.current_thinclient_to_vm_mapping OWNER TO "vdi-dbadmin";

DROP VIEW thinclient_everything_view;
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
FROM
    sysinfo_to_thinclient_mapping s
    LEFT JOIN (
        current_thinclient_to_vm_mapping c ON (((s.thinclient)::text = (c.thinclient)::text))
    )
ORDER BY
    c.prio DESC,
    c.start_date,
    c.id;
