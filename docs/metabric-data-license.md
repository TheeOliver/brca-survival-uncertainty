# METABRIC source data: license and attribution

This repository includes the four clinical-table responses used by the thesis from the public
cBioPortal study [`brca_metabric`](https://www.cbioportal.org/study?id=brca_metabric):
`study.json.gz`, `clinical_attributes.json.gz`, `clinical_patient.json.gz`, and
`clinical_sample.json.gz`. The exact snapshot was downloaded on 2026-09-29 and is recorded in
[`PROVENANCE.json`](../data/raw/cbioportal_brca_metabric/PROVENANCE.json). Verify its bytes
from the repository root with:

```bash
(cd data/raw && sha256sum -c CHECKSUMS.sha256)
```

The cBioPortal Datahub states that public datasets are made available under the
[Open Data Commons Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/)
and may be shared and modified with attribution; derived databases must remain available
under the same license. The cBioPortal [FAQ](https://docs.cbioportal.org/user-guide/faq/)
notes that restrictions, when applicable, are specified with the individual study. The public
`brca_metabric` study metadata used for this snapshot does not state a study-specific
redistribution restriction. See the [cBioPortal Datahub terms](https://github.com/cBioPortal/datahub#license)
and check the study page for current source information.

Please attribute cBioPortal and the underlying METABRIC publications:

- Curtis et al. (2012), *The genomic and transcriptomic architecture of 2,000 breast tumours reveals novel subgroups*, Nature. [PMID 22522925](https://pubmed.ncbi.nlm.nih.gov/22522925/)
- Pereira et al. (2016), *The somatic mutation profiles of 2,433 breast cancers refine their genomic and transcriptomic landscapes*, Nature Communications. [PMID 27161491](https://pubmed.ncbi.nlm.nih.gov/27161491/)
- Rueda et al. (2019), *Dynamics of breast-cancer relapse reveal late-recurring disease*, Nature. [PMID 30867590](https://pubmed.ncbi.nlm.nih.gov/30867590/)
- Cerami et al. (2012) and Gao et al. (2013), cBioPortal platform publications.

Only the public clinical API payloads used by this analysis are included. Controlled-access
expression/genomic files, derived patient-level analysis tables, individual predictions,
model objects, and generated outputs are not distributed here. The research code and thesis
analysis are separate from the upstream data and do not imply endorsement by cBioPortal or
the METABRIC study authors.
