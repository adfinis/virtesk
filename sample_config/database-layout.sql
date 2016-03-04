--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: timed_thinclient_to_vm_mapping; Type: TABLE; Schema: public; Owner: vdi-dbadmin; Tablespace: 
--

CREATE TABLE timed_thinclient_to_vm_mapping (
    vm character varying NOT NULL,
    thinclient character varying NOT NULL,
    start_date timestamp with time zone,
    end_date timestamp with time zone,
    id bigint NOT NULL,
    shutdown_vm boolean DEFAULT false NOT NULL
);


ALTER TABLE public.timed_thinclient_to_vm_mapping OWNER TO "vdi-dbadmin";

--
-- Name: current_thinclient_to_vm_mapping; Type: VIEW; Schema: public; Owner: vdi-dbadmin
--

CREATE VIEW current_thinclient_to_vm_mapping AS
    SELECT f.id, f.thinclient, f.vm, f.start_date, f.end_date, f.prio, f.shutdown_vm FROM ((SELECT timed_thinclient_to_vm_mapping.id, timed_thinclient_to_vm_mapping.thinclient, timed_thinclient_to_vm_mapping.vm, timed_thinclient_to_vm_mapping.start_date, timed_thinclient_to_vm_mapping.end_date, 0 AS prio, timed_thinclient_to_vm_mapping.shutdown_vm FROM timed_thinclient_to_vm_mapping WHERE ((timed_thinclient_to_vm_mapping.start_date IS NULL) AND (timed_thinclient_to_vm_mapping.end_date IS NULL)) UNION SELECT timed_thinclient_to_vm_mapping.id, timed_thinclient_to_vm_mapping.thinclient, timed_thinclient_to_vm_mapping.vm, timed_thinclient_to_vm_mapping.start_date, timed_thinclient_to_vm_mapping.end_date, 1 AS prio, timed_thinclient_to_vm_mapping.shutdown_vm FROM timed_thinclient_to_vm_mapping WHERE ((timed_thinclient_to_vm_mapping.start_date <= now()) AND (timed_thinclient_to_vm_mapping.end_date IS NULL))) UNION SELECT timed_thinclient_to_vm_mapping.id, timed_thinclient_to_vm_mapping.thinclient, timed_thinclient_to_vm_mapping.vm, timed_thinclient_to_vm_mapping.start_date, timed_thinclient_to_vm_mapping.end_date, 2 AS prio, timed_thinclient_to_vm_mapping.shutdown_vm FROM timed_thinclient_to_vm_mapping WHERE ((now() >= timed_thinclient_to_vm_mapping.start_date) AND (now() <= timed_thinclient_to_vm_mapping.end_date))) f ORDER BY f.prio DESC, f.start_date, f.id;


ALTER TABLE public.current_thinclient_to_vm_mapping OWNER TO "vdi-dbadmin";

--
-- Name: dhcphostname_to_thinclient_auto_mapping; Type: VIEW; Schema: public; Owner: vdi-dbadmin
--

CREATE VIEW dhcphostname_to_thinclient_auto_mapping AS
    SELECT DISTINCT (((timed_thinclient_to_vm_mapping.thinclient)::text || '.thinclients.yourdomain.site'::text))::character varying AS dhcp_hostname, timed_thinclient_to_vm_mapping.thinclient FROM timed_thinclient_to_vm_mapping UNION SELECT DISTINCT timed_thinclient_to_vm_mapping.thinclient AS dhcp_hostname, timed_thinclient_to_vm_mapping.thinclient FROM timed_thinclient_to_vm_mapping;


ALTER TABLE public.dhcphostname_to_thinclient_auto_mapping OWNER TO "vdi-dbadmin";

--
-- Name: dhcphostname_to_thinclient_mapping; Type: TABLE; Schema: public; Owner: vdi-dbadmin; Tablespace: 
--

CREATE TABLE dhcphostname_to_thinclient_mapping (
    dhcp_hostname character varying NOT NULL,
    thinclient character varying NOT NULL
);


ALTER TABLE public.dhcphostname_to_thinclient_mapping OWNER TO "vdi-dbadmin";

--
-- Name: systemuuid_to_thinclient_mapping; Type: TABLE; Schema: public; Owner: vdi-dbadmin; Tablespace: 
--

CREATE TABLE systemuuid_to_thinclient_mapping (
    systemuuid character varying NOT NULL,
    thinclient character varying NOT NULL
);


ALTER TABLE public.systemuuid_to_thinclient_mapping OWNER TO "vdi-dbadmin";

--
-- Name: sysinfo_to_thinclient_mapping; Type: VIEW; Schema: public; Owner: vdi-dbadmin
--

CREATE VIEW sysinfo_to_thinclient_mapping AS
    SELECT f.dhcp_hostname, f.systemuuid, f.thinclient, f.prio FROM ((SELECT dhcphostname_to_thinclient_auto_mapping.dhcp_hostname, NULL::character varying AS systemuuid, dhcphostname_to_thinclient_auto_mapping.thinclient, 100 AS prio FROM dhcphostname_to_thinclient_auto_mapping UNION SELECT dhcphostname_to_thinclient_mapping.dhcp_hostname, NULL::character varying AS systemuuid, dhcphostname_to_thinclient_mapping.thinclient, 200 AS prio FROM dhcphostname_to_thinclient_mapping) UNION SELECT NULL::character varying AS dhcp_hostname, systemuuid_to_thinclient_mapping.systemuuid, systemuuid_to_thinclient_mapping.thinclient, 300 AS prio FROM systemuuid_to_thinclient_mapping) f ORDER BY f.prio DESC;


ALTER TABLE public.sysinfo_to_thinclient_mapping OWNER TO "vdi-dbadmin";

--
-- Name: thinclient_everything_view; Type: VIEW; Schema: public; Owner: vdi-dbadmin
--

CREATE VIEW thinclient_everything_view AS
    SELECT DISTINCT s.thinclient, c.vm, s.dhcp_hostname, s.systemuuid, c.id, c.start_date, c.end_date, c.prio, c.shutdown_vm FROM (sysinfo_to_thinclient_mapping s LEFT JOIN current_thinclient_to_vm_mapping c ON (((s.thinclient)::text = (c.thinclient)::text))) ORDER BY c.prio DESC, c.start_date, c.id;


ALTER TABLE public.thinclient_everything_view OWNER TO "vdi-dbadmin";

--
-- Name: timed_thinclient_to_vm_mapping_id_seq; Type: SEQUENCE; Schema: public; Owner: vdi-dbadmin
--

CREATE SEQUENCE timed_thinclient_to_vm_mapping_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.timed_thinclient_to_vm_mapping_id_seq OWNER TO "vdi-dbadmin";

--
-- Name: timed_thinclient_to_vm_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vdi-dbadmin
--

ALTER SEQUENCE timed_thinclient_to_vm_mapping_id_seq OWNED BY timed_thinclient_to_vm_mapping.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: vdi-dbadmin
--

ALTER TABLE ONLY timed_thinclient_to_vm_mapping ALTER COLUMN id SET DEFAULT nextval('timed_thinclient_to_vm_mapping_id_seq'::regclass);


--
-- Name: dhcphostname_to_thinclient_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: vdi-dbadmin; Tablespace: 
--

ALTER TABLE ONLY dhcphostname_to_thinclient_mapping
    ADD CONSTRAINT dhcphostname_to_thinclient_mapping_pkey PRIMARY KEY (dhcp_hostname);


--
-- Name: systemuuid_to_thinclient_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: vdi-dbadmin; Tablespace: 
--

ALTER TABLE ONLY systemuuid_to_thinclient_mapping
    ADD CONSTRAINT systemuuid_to_thinclient_mapping_pkey PRIMARY KEY (systemuuid);


--
-- Name: timed_thinclient_to_vm_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: vdi-dbadmin; Tablespace: 
--

ALTER TABLE ONLY timed_thinclient_to_vm_mapping
    ADD CONSTRAINT timed_thinclient_to_vm_mapping_pkey PRIMARY KEY (id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: thinclient_everything_view; Type: ACL; Schema: public; Owner: vdi-dbadmin
--

REVOKE ALL ON TABLE thinclient_everything_view FROM PUBLIC;
REVOKE ALL ON TABLE thinclient_everything_view FROM "vdi-dbadmin";
GRANT ALL ON TABLE thinclient_everything_view TO "vdi-dbadmin";
GRANT SELECT ON TABLE thinclient_everything_view TO "vdi-readonly";


--
-- PostgreSQL database dump complete
--

