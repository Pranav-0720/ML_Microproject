# Dataset sources

| Source | Files in data/raw | Shape | Purpose | License and limitations |
|---|---|---:|---|---|
| [Indian Government Welfare Schemes](https://www.kaggle.com/datasets/premsargara/indian-government-beneficiary-schemes) | welfare-schemes.zip, indian_government_schemes.csv | 4,702 × 29 | Selected catalog for search and dashboard statistics | Kaggle API reports MIT. Several inferred or structured eligibility fields are sparse. No applicant outcome labels. |
| [Indian government central sector scheme](https://www.kaggle.com/datasets/mrsumitjha/indian-government-central-sector-scheme) | central-sector.zip, CenterSectorScheme2021-22.csv | 772 × 16 | Historical budget data, inspected as an alternative | Kaggle lists Data files © Original Authors. Contains fiscal aggregates and summary rows. No applicant outcome labels. |

Both public ZIPs were downloaded from Kaggle's official dataset API and extracted locally. Run
`python -m src.data_loader` for the per-column missing-value and exact duplicate
counts. The report is saved to `data/processed/raw_audit.json`. Empty strings and
Pandas' standard missing-value markers count as missing. Common markers such as ` NA` also count after trimming whitespace. Publisher placeholders
outside that definition may still occur.


### Restore the downloaded archives

From the project root in PowerShell, run the following if the local raw files are missing.

```powershell
New-Item -ItemType Directory -Force data/raw | Out-Null
curl.exe -fL https://www.kaggle.com/api/v1/datasets/download/premsargara/indian-government-beneficiary-schemes -o data/raw/welfare-schemes.zip
curl.exe -fL https://www.kaggle.com/api/v1/datasets/download/mrsumitjha/indian-government-central-sector-scheme -o data/raw/central-sector.zip
Expand-Archive -LiteralPath data/raw/welfare-schemes.zip -DestinationPath data/raw
Expand-Archive -LiteralPath data/raw/central-sector.zip -DestinationPath data/raw
```

## Official sources and reviewed rules

Reviewed 21 November 2026. The app ships a small, separately maintained rule catalog.

- [myScheme](https://www.myscheme.gov.in/) is the government scheme discovery portal. Its [PM Ujjwala 2.0 profile](https://www.myscheme.gov.in/schemes/pmuy2) corroborates the age and household LPG conditions.
- [Open Government Data India](https://www.data.gov.in/) was consulted for public data context.
- [PM Ujjwala 2.0](https://pmuy.gov.in/Ujjwala2.html) documents age, household LPG, applicant gender, deprivation declaration and application documents.
- [PM-KISAN operational guidelines](https://pmkisan.gov.in/Documents/RevisedPM-KISANOperationalGuidelines%28English%29.pdf) document cultivable land ownership, exclusions, land-record requirements and special cases. The app defers land verification to the authority.
- [MahaDBT DTE scheme](https://mahadbt.maharashtra.gov.in/SchemeData/SchemeData?str=E9DDFA703C38E51A7F4D327BDEB7125DE0BA4AE1C51180C272281017EBEF6F7C) covers Maharashtra domicile, family income and technical-education conditions. Admission, institutions, other benefits, family caps and academic requirements require manual verification.

## Synthetic data

`synthetic_training.csv` contains generated profile–scheme pairs. The binary target
means no known failure on the subset of reviewed rules represented by the model
features. The underlying eligibility decision remains a separate rule-based check.
The synthetic population and missingness are illustrative and cannot establish
performance or fairness on real applicants. `synthetic_clusters.csv` contains one
row per generated profile with cluster and PCA coordinates.