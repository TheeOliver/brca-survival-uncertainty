# METABRIC data dictionary

## Source and provenance

| | |
| --- | --- |
| Source | cBioPortal REST API, study `brca_metabric` — *Breast Cancer (METABRIC, Nature 2012 & Nat Commun 2016)* |
| Access | **public study** (`publicStudy: true`); clinical tables only |
| cBioPortal import date | 2026-01-05 |
| Downloaded | 2026-09-29 by `scripts/00_download_data.py` (`make download`) |
| Raw snapshot | `data/raw/cbioportal_brca_metabric/` — gzipped API JSON + `PROVENANCE.json` |
| Checksums | `data/raw/CHECKSUMS.sha256` (committed; `cd data/raw && sha256sum -c CHECKSUMS.sha256`) |
| Cite | Curtis et al. 2012 (PMID 22522925), Pereira et al. 2016 (27161491), Rueda et al. 2019 (30867590), and cBioPortal (Cerami 2012, Gao 2013) |

Expression and raw genomic data remain controlled-access at EGA `EGAS00000000083`; this thesis
does not need them (PAM50 is provided as a label). Public availability does **not** make this
repo a redistribution point: patient-level files under `data/` stay ignored, while the raw
snapshot checksum manifest is committed. Patient rows never enter Git.

`data/raw/` is immutable — `make download` refuses to overwrite an existing snapshot.

## Cohort (aggregates from the 2026-09-29 snapshot)

| | n |
| --- | --- |
| Patients in study (1 sample each, all female) | 2,509 |
| With overall-survival outcome **and** PAM50 | 1,981 |
| Complete cases: all predictors + PAM50 + OS | 1,815 |

The 528 patients without outcome are the 2016 targeted-sequencing extension: no survival, no
PAM50, no PR/HER2. They cannot enter a survival model and are excluded at stage 01. The 1,981
match the published ~1,980-tumour METABRIC cohort.

Outcome summary (n = 1,981): 1,144 deaths (57.7%), of which **646 died of disease and 497 of
other causes**; median follow-up 196 months (reverse Kaplan-Meier); maximum 355 months. Relapse
status is available for 2,488 patients (1,002 recurred).

Kaplan-Meier median overall survival by subtype (months): claudin-low 219, LumA 187, Normal 159,
Basal 131, LumB 123, Her2 107. The ordering of LumA above Basal and Her2 matches the published
prognostic ordering, which is evidence the fields are mapped correctly.

## Source → schema mapping

| Schema column | cBioPortal attribute | Level | Notes |
| --- | --- | --- | --- |
| `patient_id` | `patientId` | patient | unique; 1 sample per patient |
| `survival_months` | `OS_MONTHS` | patient | months for both DSS and OS |
| `event` (OS) | `OS_STATUS` `1:DECEASED` / `0:LIVING` | patient | all-cause death indicator |
| `event` (DSS) | `VITAL_STATUS` | patient | Died of Disease; other-cause death is censored |
| `age_at_diagnosis` | `AGE_AT_DIAGNOSIS` | patient | years; 0 missing |
| `tumor_size` | `TUMOR_SIZE` | sample | mm; string in API → float; 25 missing |
| `tumor_grade` | `GRADE` | sample | 1 / 2 / 3; 87 missing |
| `lymph_nodes_positive` | `LYMPH_NODES_EXAMINED_POSITIVE` | patient | string in API → int; 76 missing |
| `er_status` | `ER_STATUS` | sample | Positive / Negative (`ER_IHC` is the IHC-only variant) |
| `pr_status` | `PR_STATUS` | sample | |
| `her2_status` | `HER2_STATUS` | sample | (`HER2_SNP6` is the copy-number variant) |
| `pam50_subtype` | `CLAUDIN_SUBTYPE` | patient | LumA 700, LumB 475, Her2 224, claudin-low 218, Basal 209, Normal 148, NC 6; 1 missing |

Missing counts are within the 1,979-patient analysis cohort (1,981 with OS, minus one missing
cause of death and one with `OS_MONTHS <= 0`). PR, HER2 and PAM50 each have 1 missing. Also
missing but outside the design: `TUMOR_STAGE` 26.0%, `THREEGENE` 11.0%, `LATERALITY` 5.6%,
`CELLULARITY` 3.2%.

Also available but outside the current design: treatment (`CHEMOTHERAPY`, `HORMONE_THERAPY`,
`RADIO_THERAPY`, `BREAST_SURGERY`), `NPI`, `INTCLUST`, `TUMOR_STAGE`, `CELLULARITY`,
`INFERRED_MENOPAUSAL_STATE`, `COHORT` (recruitment site 1–9). Treatment variables are
post-diagnosis decisions; including them as predictors needs thought (they partly encode the
clinician's own prognosis).

## Cohort and encoding choices

I use DSS as the primary endpoint and OS as a sensitivity analysis. Starting from the
1,981 patients with outcome and PAM50 information, I exclude one without usable
cause-of-death classification and one with nonpositive follow-up. The 1,979-patient
analysis cohort has 646 observed DSS events. Other-cause deaths are censored for DSS;
this is a net-survival analysis under censoring assumptions, not a competing-risk
cumulative-incidence model.

I keep claudin-low separate, encode NC or missing subtype as unknown, and fit all
imputation and scaling on training patients only. I retain full follow-up for fitting;
the 300- and 120-month conformal targets are restricted prediction horizons, not
administrative truncation of the fitting outcome. The reasoning and limitations are
recorded in [analysis decisions](analysis-decisions.md).
