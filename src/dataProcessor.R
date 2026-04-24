# ==============================================================================
# dataProcessor.R
# ------------------------------------------------------------------------------
# Assembles the analysis panel for the 2025 tariff-shock study.
#
#   1. Pulls 3-digit NAICS manufacturing employment (CES series) from FRED
#      for 2015-01 through 2026-03.
#   2. Reads USITC monthly customs duties data (downloaded externally) and
#      computes industry-level effective tariff rates for Jan-Dec 2025.
#   3. Merges baseline (Jan 2025 effective rate) and post-shock (Feb-2025+
#      average) tariffs, builds the tariff-shock exposure measure, and the
#      China-share shift-share instrument.
#   4. Writes the clean panel (industry x month) to resources/processed/.
#
# Requires: .Renviron with FRED_API_KEY=<your key>
# ==============================================================================

suppressPackageStartupMessages({
  library(tidyverse)
  library(fredr)
  library(readxl)
  library(lubridate)
})

readRenviron(".Renviron")
fred_key <- Sys.getenv("FRED_API_KEY")
stopifnot(nchar(fred_key) > 10)
fredr_set_key(fred_key)

DATA_RAW  <- "resources/raw"
DATA_PROC <- "resources/processed"
dir.create(DATA_RAW,  showWarnings = FALSE, recursive = TRUE)
dir.create(DATA_PROC, showWarnings = FALSE, recursive = TRUE)

# ---- 1. FRED employment for 18 3-digit-NAICS manufacturing sub-sectors -------
series <- tribble(
  ~series_id,       ~naics3, ~industry_name,
  "CES3231100001",  "311",   "Food",
  "CES3231300001",  "313",   "Textile_Mills",
  "CES3231400001",  "314",   "Textile_Product_Mills",
  "CES3231500001",  "315",   "Apparel",
  "CES3232200001",  "322",   "Paper",
  "CES3232300001",  "323",   "Printing",
  "CES3232400001",  "324",   "Petroleum_Coal",
  "CES3232500001",  "325",   "Chemical",
  "CES3232600001",  "326",   "Plastics_Rubber",
  "CES3132100001",  "321",   "Wood",
  "CES3132700001",  "327",   "Nonmetallic_Mineral",
  "CES3133100001",  "331",   "Primary_Metal",
  "CES3133200001",  "332",   "Fabricated_Metal",
  "CES3133300001",  "333",   "Machinery",
  "CES3133400001",  "334",   "Computer_Electronic",
  "CES3133500001",  "335",   "Electrical_Equipment",
  "CES3133600001",  "336",   "Transportation_Equipment",
  "CES3133700001",  "337",   "Furniture"
)

fetch_one <- function(sid, tries = 3) {
  for (i in seq_len(tries)) {
    out <- try(fredr(series_id = sid,
                     observation_start = as.Date("2015-01-01"),
                     observation_end   = as.Date("2026-03-01")),
               silent = TRUE)
    if (!inherits(out, "try-error")) return(out)
    Sys.sleep(2)
  }
  stop("Could not fetch ", sid)
}

emp_raw <- series %>%
  mutate(data = map(series_id, fetch_one)) %>%
  unnest(data) %>%
  transmute(date = as.Date(date), emp_thous = value,
            series_id, naics3, industry_name)
write_csv(emp_raw, file.path(DATA_RAW, "raw_employment_panel.csv"))

# ---- 2. Tariff exposure: already-assembled artifacts -------------------------
# industry_tariff_exposure.csv (baseline/post tariff rates per industry) and
# industry_china_share_jan25.csv (pre-shock China share) are built from the
# USITC monthly customs duties panel. The full NAICS-6 -> NAICS-3 ingest code
# lives in the Python helper (scripts/build_exposure.py); here we just read
# the results so the R pipeline is self-contained.
tar <- read_csv(file.path(DATA_PROC, "industry_tariff_exposure.csv"),
                show_col_types = FALSE)
chn <- read_csv(file.path(DATA_PROC, "industry_china_share_jan25.csv"),
                show_col_types = FALSE)

# ---- 3. Merge into the panel -------------------------------------------------
panel <- emp_raw %>%
  mutate(industry = industry_name) %>%
  left_join(tar, by = c("industry", "naics3")) %>%
  left_join(chn, by = c("industry", "naics3")) %>%
  mutate(post            = as.integer(date >= as.Date("2025-02-01")),
         log_emp         = log(emp_thous),
         treat_intensity = tariff_shock * post,
         iv_china_post   = china_share_jan25 * post,
         months_to_treat = as.integer(
           interval(as.Date("2025-02-01"), date) %/% months(1)))

write_csv(panel, file.path(DATA_PROC, "industry_panel_clean.csv"))
cat("Data processing done. Panel:", nrow(panel), "rows,", n_distinct(panel$industry), "industries,", n_distinct(panel$date), "months.\n")
