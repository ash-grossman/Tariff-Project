# ECO 4370 - Do Tariffs Kill Manufacturing Jobs? (2025 Evidence)

A short empirical paper estimating the employment effects of the February 2025
U.S. tariff shock on 18 3-digit NAICS manufacturing sub-sectors, using a
two-way fixed-effects DiD and a shift-share 2SLS identification strategy.

## Research question
What is the effect of the 2025 U.S. tariff shock on manufacturing employment,
and does the answer change once we account for the likelihood that tariff
assignment was not random across industries?

## Data sources

| Source | Vintage | Use |
|---|---|---|
| FRED Current Employment Statistics (CES) | Jan 2015 - Mar 2026 (monthly, SA) | `emp_thous`: All-employees head count for 18 3-digit NAICS manufacturing sub-sectors (series `CES31xxxxxxxx` and `CES32xxxxxxxx`). |
| USITC DataWeb monthly customs duties | Jan-Dec 2025 | `eff_tariff_rate` = Calculated Duties / Customs Value, aggregated to NAICS-3 and month. Used for baseline/post tariffs, the tariff shock, and the January 2025 China import share. |

FRED series IDs are listed in `src/dataProcessor.R`. The USITC extract is
expected at `resources/raw/monthly_customs_duties_2025.xlsx` (ignored from git
because it is ~22 MB; re-download from https://dataweb.usitc.gov).

## Repo structure

```
ECO4370-Project/
  .Renviron                      # FRED_API_KEY=<your key>  (not committed)
  .gitignore
  README.md
  ECO4370-Project.Rproj
  Project.qmd                    # Quarto wrapper (optional)
  src/
    dataProcessor.R              # FRED + USITC ingest -> clean panel
    didModel.R                   # TWFE DiD + event study
    ivModel.R                    # Shift-share 2SLS + robustness
    figures.R                    # Descriptive figures
  resources/
    raw/
      raw_employment_panel.csv
      monthly_customs_duties_2025.xlsx   # externally downloaded
    processed/
      industry_panel_clean.csv           # main analysis panel
      industry_tariff_exposure.csv
      industry_monthly_tariff_2025.csv
      industry_china_share_jan25.csv
  output/
    model_results.json
    figures/
      fig1_event_study.png
      fig2_emp_trends.png
      fig3_coefficient_compare.png
      fig4_scatter.png
    tables/
      main_results.{csv,tex}
      robustness.{csv,tex}
      did_results.tex
      iv_comparison.tex
      event_study_coefs.csv
      industry_summary.csv
  report/
    ECO4370_Final_Report.pdf     # publishable writeup
```

## Reproducibility

1. Put your FRED API key 