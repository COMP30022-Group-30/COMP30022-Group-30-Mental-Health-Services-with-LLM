-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.campus (
  campus_key uuid NOT NULL DEFAULT gen_random_uuid(),
  organisation_key uuid NOT NULL,
  campus_name text NOT NULL,
  CONSTRAINT campus_pkey PRIMARY KEY (campus_key),
  CONSTRAINT campus_organisation_key_fkey FOREIGN KEY (organisation_key) REFERENCES public.organisation(organisation_key)
);
CREATE TABLE public.cost (
  cost_key uuid NOT NULL DEFAULT gen_random_uuid(),
  service_campus_key uuid NOT NULL,
  cost_num integer NOT NULL,
  CONSTRAINT cost_pkey PRIMARY KEY (cost_key),
  CONSTRAINT cost_cost_num_fkey FOREIGN KEY (cost_num) REFERENCES public.cost_lookup(cost_num),
  CONSTRAINT cost_service_campus_key_fkey FOREIGN KEY (service_campus_key) REFERENCES public.service_campus(service_campus_key)
);
CREATE TABLE public.cost_lookup (
  cost_num integer NOT NULL,
  cost text NOT NULL,
  CONSTRAINT cost_lookup_pkey PRIMARY KEY (cost_num)
);
CREATE TABLE public.delivery_method (
  delivery_method_key uuid NOT NULL DEFAULT gen_random_uuid(),
  service_campus_key uuid NOT NULL,
  delivery_method_num integer NOT NULL,
  CONSTRAINT delivery_method_pkey PRIMARY KEY (delivery_method_key),
  CONSTRAINT delivery_method_delivery_method_num_fkey FOREIGN KEY (delivery_method_num) REFERENCES public.delivery_method_lookup(delivery_method_num),
  CONSTRAINT delivery_method_service_campus_key_fkey FOREIGN KEY (service_campus_key) REFERENCES public.service_campus(service_campus_key)
);
CREATE TABLE public.delivery_method_lookup (
  delivery_method_num integer NOT NULL,
  delivery_method text NOT NULL,
  CONSTRAINT delivery_method_lookup_pkey PRIMARY KEY (delivery_method_num)
);
CREATE TABLE public.level_of_care (
  level_of_care_key uuid NOT NULL DEFAULT gen_random_uuid(),
  service_campus_key uuid NOT NULL,
  level_of_care_num integer,
  CONSTRAINT level_of_care_pkey PRIMARY KEY (level_of_care_key),
  CONSTRAINT level_of_care_service_campus_key_fkey FOREIGN KEY (service_campus_key) REFERENCES public.service_campus(service_campus_key),
  CONSTRAINT level_of_care_level_of_care_num_fkey FOREIGN KEY (level_of_care_num) REFERENCES public.level_of_care_lookup(level_of_care_num)
);
CREATE TABLE public.level_of_care_lookup (
  level_of_care_num integer NOT NULL,
  level_of_care text NOT NULL,
  CONSTRAINT level_of_care_lookup_pkey PRIMARY KEY (level_of_care_num)
);
CREATE TABLE public.organisation (
  organisation_key uuid NOT NULL DEFAULT gen_random_uuid(),
  organisation_name text NOT NULL UNIQUE,
  CONSTRAINT organisation_pkey PRIMARY KEY (organisation_key)
);
CREATE TABLE public.postcode (
  postcode_key uuid NOT NULL DEFAULT gen_random_uuid(),
  region_key uuid NOT NULL,
  postcode text NOT NULL,
  CONSTRAINT postcode_pkey PRIMARY KEY (postcode_key),
  CONSTRAINT postcode_region_key_fkey FOREIGN KEY (region_key) REFERENCES public.region(region_key)
);
CREATE TABLE public.referral_pathway (
  referral_pathway_key uuid NOT NULL DEFAULT gen_random_uuid(),
  service_campus_key uuid NOT NULL,
  referral_pathway_num integer NOT NULL,
  CONSTRAINT referral_pathway_pkey PRIMARY KEY (referral_pathway_key),
  CONSTRAINT referral_pathway_referral_pathway_num_fkey FOREIGN KEY (referral_pathway_num) REFERENCES public.referral_pathway_lookup(referral_pathway_num),
  CONSTRAINT referral_pathway_service_campus_key_fkey FOREIGN KEY (service_campus_key) REFERENCES public.service_campus(service_campus_key)
);
CREATE TABLE public.referral_pathway_lookup (
  referral_pathway_num integer NOT NULL,
  referral_pathway text NOT NULL,
  CONSTRAINT referral_pathway_lookup_pkey PRIMARY KEY (referral_pathway_num)
);
CREATE TABLE public.region (
  region_key uuid NOT NULL DEFAULT gen_random_uuid(),
  region_name text NOT NULL UNIQUE,
  CONSTRAINT region_pkey PRIMARY KEY (region_key)
);
CREATE TABLE public.service (
  service_key uuid NOT NULL DEFAULT gen_random_uuid(),
  organisation_key uuid NOT NULL,
  service_name text NOT NULL,
  CONSTRAINT service_pkey PRIMARY KEY (service_key),
  CONSTRAINT service_organisation_key_fkey FOREIGN KEY (organisation_key) REFERENCES public.organisation(organisation_key)
);
CREATE TABLE public.service_campus (
  service_campus_key uuid NOT NULL DEFAULT gen_random_uuid(),
  service_key uuid NOT NULL,
  campus_key uuid NOT NULL,
  email text,
  phone text,
  website text,
  notes text,
  expected_wait_time text,
  op_hours_24_7 boolean,
  op_hours_standard boolean,
  op_hours_extended boolean,
  op_hours_extended_details text,
  address text,
  suburb text,
  state text,
  postcode text,
  eligibility_and_description text,
  CONSTRAINT service_campus_pkey PRIMARY KEY (service_campus_key),
  CONSTRAINT service_campus_campus_key_fkey FOREIGN KEY (campus_key) REFERENCES public.campus(campus_key),
  CONSTRAINT service_campus_service_key_fkey FOREIGN KEY (service_key) REFERENCES public.service(service_key)
);
CREATE TABLE public.service_region (
  service_campus_key uuid NOT NULL,
  region_key uuid NOT NULL,
  CONSTRAINT service_region_pkey PRIMARY KEY (service_campus_key, region_key),
  CONSTRAINT service_region_region_key_fkey FOREIGN KEY (region_key) REFERENCES public.region(region_key),
  CONSTRAINT service_region_service_campus_key_fkey FOREIGN KEY (service_campus_key) REFERENCES public.service_campus(service_campus_key)
);
CREATE TABLE public.service_type (
  service_type_key uuid NOT NULL DEFAULT gen_random_uuid(),
  service_campus_key uuid NOT NULL,
  service_type_num integer,
  CONSTRAINT service_type_pkey PRIMARY KEY (service_type_key),
  CONSTRAINT service_type_service_type_num_fkey FOREIGN KEY (service_type_num) REFERENCES public.service_type_lookup(service_type_num),
  CONSTRAINT service_type_service_campus_key_fkey FOREIGN KEY (service_campus_key) REFERENCES public.service_campus(service_campus_key)
);
CREATE TABLE public.service_type_lookup (
  service_type_num integer NOT NULL,
  service_type text NOT NULL,
  CONSTRAINT service_type_lookup_pkey PRIMARY KEY (service_type_num)
);
CREATE TABLE public.spatial_ref_sys (
  srid integer NOT NULL CHECK (srid > 0 AND srid <= 998999),
  auth_name character varying,
  auth_srid integer,
  srtext character varying,
  proj4text character varying,
  CONSTRAINT spatial_ref_sys_pkey PRIMARY KEY (srid)
);
CREATE TABLE public.staging_services (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  organisation_name text,
  campus_name text,
  service_name text,
  region_name text,
  email text,
  phone text,
  website text,
  notes text,
  expected_wait_time text,
  opening_hours_24_7 boolean,
  opening_hours_standard boolean,
  opening_hours_extended boolean,
  op_hours_extended_details text,
  address text,
  suburb text,
  state text,
  postcode text,
  cost text,
  delivery_method text,
  level_of_care text,
  referral_pathway text,
  service_type text,
  target_population text,
  workforce_type text,
  location USER-DEFINED,
  embedding USER-DEFINED,
  CONSTRAINT staging_services_pkey PRIMARY KEY (id)
);
CREATE TABLE public.target_population (
  target_population_key uuid NOT NULL DEFAULT gen_random_uuid(),
  service_campus_key uuid NOT NULL,
  target_population_num integer,
  CONSTRAINT target_population_pkey PRIMARY KEY (target_population_key),
  CONSTRAINT target_population_target_population_num_fkey FOREIGN KEY (target_population_num) REFERENCES public.target_population_lookup(target_population_num),
  CONSTRAINT target_population_service_campus_key_fkey FOREIGN KEY (service_campus_key) REFERENCES public.service_campus(service_campus_key)
);
CREATE TABLE public.target_population_lookup (
  target_population_num integer NOT NULL,
  target_population text NOT NULL,
  CONSTRAINT target_population_lookup_pkey PRIMARY KEY (target_population_num)
);
CREATE TABLE public.workforce_type (
  workforce_type_key uuid NOT NULL DEFAULT gen_random_uuid(),
  service_campus_key uuid NOT NULL,
  workforce_type_num integer NOT NULL,
  CONSTRAINT workforce_type_pkey PRIMARY KEY (workforce_type_key),
  CONSTRAINT workforce_type_workforce_type_num_fkey FOREIGN KEY (workforce_type_num) REFERENCES public.workforce_type_lookup(workforce_type_num),
  CONSTRAINT workforce_type_service_campus_key_fkey FOREIGN KEY (service_campus_key) REFERENCES public.service_campus(service_campus_key)
);
CREATE TABLE public.workforce_type_lookup (
  workforce_type_num integer NOT NULL,
  workforce_type text NOT NULL,
  CONSTRAINT workforce_type_lookup_pkey PRIMARY KEY (workforce_type_num)
);