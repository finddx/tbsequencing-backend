-- One Patient <-> Many Sample
CREATE TABLE "patient" (
  "patient_id" bigserial primary key,
  "gender" char(1),
  "age_at_sampling" int,
  "disease" varchar,
  "new_tuberculosis_case" boolean,
  "previous_treatment_category" varchar,
  "treatment_regimen" varchar,
  "treatment_duration" int,
  "treatment_outcome" varchar,
  "hiv_positive" boolean
);


-- Staging table for both link between variant id and new annotation values
-- All new incoming data is copied here before final insertion
-- Only new annotations and new links between variants and new anotations are inserted
-- For VariantToAnnotation insertion, JOINS are performed to insert the Ids of each componenent
CREATE TABLE "staged_variant_to_annotation" (
  "variant_id" int NOT NULL,
  "locus_tag_name" varchar NOT NULL,
  "hgvs_value" varchar NOT NULL,
  "predicted_effect" varchar NOT NULL,
  "type" varchar NOT NULL,
  "distance_to_reference" int
  );


-- Staging table for Genotypes
-- Incomming data is copied here then inserted after JOINING with "variant"
CREATE TABLE "staged_genotype" (
  "sample_id" integer NOT NULL,
  "chromosome" varchar NOT NULL,
  "position" int NOT NULL,
  "variant_id" int,
  "reference_nucleotide" varchar NOT NULL,
  "alternative_nucleotide" varchar NOT NULL,
  "genotyper" varchar NOT NULL,
  "quality" float NOT NULL,
  "reference_ad" int NOT NULL,
  "alternative_ad" int NOT NULL,
  "total_dp" int NOT NULL,
  "genotype_value" varchar NOT NULL
);


-- Target of the targeted Next Generation Sequencing kits
CREATE TABLE "amplicon_target" (
  "amplicon_target_id" serial primary key,
  "amplicon_assay_name" varchar,
  "chromosome" varchar NOT NULL,
  "start" int NOT NULL,
  "end" int  NOT NULL,
  "gene_db_crossref_id" int NOT NULL REFERENCES biosql.dbxref (dbxref_id)
);


-- TODO remove or transfer under Django?
CREATE TABLE "phenotypic_drug_susceptiblity_test_who_category" (
    "drug_id" integer NOT NULL,
    "medium_id" integer NOT NULL,
    "concentration" float NOT NULL,
    "category" varchar NOT NULL,
    UNIQUE("drug_id", "medium_id", "concentration"),
    UNIQUE("drug_id", "medium_id", "category")
);


CREATE TABLE "promoter_distance" (
  "gene_db_crossref_id" integer NOT NULL REFERENCES biosql.dbxref (dbxref_id),
  "region_start" integer NOT NULL,
  "region_end" integer NOT NULL,
  UNIQUE("gene_db_crossref_id", "region_start", "region_end")
);
