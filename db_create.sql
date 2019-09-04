--
-- PostgreSQL database dump
--

-- Dumped from database version 10.10
-- Dumped by pg_dump version 10.10

-- Started on 2019-09-04 06:34:11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2823 (class 0 OID 0)
-- Dependencies: 2822
-- Name: DATABASE katastar_db; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON DATABASE katastar_db IS 'cene stanova iz katastra';


--
-- TOC entry 1 (class 3079 OID 12924)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2825 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 198 (class 1259 OID 16420)
-- Name: katastri; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.katastri (
    id integer NOT NULL,
    opstina_id integer,
    ime text NOT NULL
);


--
-- TOC entry 196 (class 1259 OID 16394)
-- Name: nekretnine; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.nekretnine (
    id integer NOT NULL,
    datum date NOT NULL,
    cena integer NOT NULL,
    kvadratura integer NOT NULL,
    cenam2 numeric NOT NULL,
    lat numeric,
    lon numeric,
    garaze integer DEFAULT 0,
    katastar_id integer
);


--
-- TOC entry 2826 (class 0 OID 0)
-- Dependencies: 196
-- Name: COLUMN nekretnine.garaze; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.nekretnine.garaze IS 'broj garaza kupljenih sa stanom';


--
-- TOC entry 197 (class 1259 OID 16412)
-- Name: opstine; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.opstine (
    id integer NOT NULL,
    ime text NOT NULL
);


--
-- TOC entry 199 (class 1259 OID 16444)
-- Name: v_nekretnine; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_nekretnine AS
 SELECT n.datum,
    n.cena,
    n.kvadratura,
    n.cenam2 AS "cena po kvadratu",
    n.garaze AS "broj garaza",
    o.ime AS opstina,
    k.ime AS "katastarska opstina",
    n.lat AS latitude,
    n.lon AS longitude
   FROM ((public.nekretnine n
     JOIN public.katastri k ON ((n.katastar_id = k.id)))
     JOIN public.opstine o ON ((k.opstina_id = o.id)));


--
-- TOC entry 2827 (class 0 OID 0)
-- Dependencies: 199
-- Name: VIEW v_nekretnine; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.v_nekretnine IS 'view koji objedinjuje sve tri glavne tabele';


--
-- TOC entry 2692 (class 2606 OID 16427)
-- Name: katastri katastar_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.katastri
    ADD CONSTRAINT katastar_pkey PRIMARY KEY (id);


--
-- TOC entry 2687 (class 2606 OID 16401)
-- Name: nekretnine nekretnina_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nekretnine
    ADD CONSTRAINT nekretnina_pkey PRIMARY KEY (id);


--
-- TOC entry 2689 (class 2606 OID 16419)
-- Name: opstine opstina_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.opstine
    ADD CONSTRAINT opstina_pkey PRIMARY KEY (id);


--
-- TOC entry 2684 (class 1259 OID 16439)
-- Name: fki_katastar_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_katastar_id ON public.nekretnine USING btree (katastar_id);


--
-- TOC entry 2690 (class 1259 OID 16433)
-- Name: fki_opstina_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_opstina_id ON public.katastri USING btree (opstina_id);


--
-- TOC entry 2685 (class 1259 OID 16402)
-- Name: index_cenam2; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_cenam2 ON public.nekretnine USING btree (cenam2 DESC NULLS LAST);


--
-- TOC entry 2693 (class 2606 OID 16434)
-- Name: nekretnine katastar_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nekretnine
    ADD CONSTRAINT katastar_id FOREIGN KEY (katastar_id) REFERENCES public.katastri(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2694 (class 2606 OID 16428)
-- Name: katastri opstina_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.katastri
    ADD CONSTRAINT opstina_id FOREIGN KEY (opstina_id) REFERENCES public.opstine(id) ON UPDATE CASCADE ON DELETE CASCADE;


-- Completed on 2019-09-04 06:34:13

--
-- PostgreSQL database dump complete
--

