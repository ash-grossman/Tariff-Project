# ==============================================================================
# didModel.R
# ------------------------------------------------------------------------------
# Two-way fixed-effects difference-in-differences of the 2025 tariff shock on
# 3-digit NAICS manufacturing log employment, plus an event study.
#
#   Model:   log_emp_it = alpha_i + gamma_t + beta * (tariff_shock_i * post_t) + e_it
#   Cluster: robust SEs at the industry (i) level.
#
# Output: output/tables/did_results.csv
#         output/tables/event_study_coefs.csv
#         output/figures/fig1_event_study.png
# ==============================================================================

suppressPackageStartupMessages({
  library(tidyverse)
  library(fixest)
  library(ggplot2)
})

df <- read_csv("resources/processed/industry_panel_clean.csv", show_col_types = FALSE)

did_full <- feols(log_emp ~ treat_intensity | industry + date,
                  data    = df,
                  cluster = ~ industry)
cat("\n--- DiD full sample ---\n"); print(summary(did_full))

sec232 <- c("Primary_Metal", "Fabricated_Metal", "Transportation_Equipment")
did_no232 <- feols(log_emp ~ treat_intensity | industry + date,
                   data    = filter(df, !(industry %in% sec232)),
                   cluster = ~ industry)
cat("\n--- DiD no-232 sample ---\n"); print(summary(did_no232))

df_es <- df %>% mutate(rel = pmax(pmin(months_to_treat, 14), -12))

es_model <- feols(log_emp ~ i(rel, tariff_shock, ref = -1) | industry + date,
                  data    = df_es,
                  cluster = ~ industry)

es_coefs <- broom::tidy(es_model) %>%
  mutate(k = as.integer(gsub("rel::|:tariff_shock", "", term))) %>%
  select(k, coef = estimate, se = std.error) %>%
  bind_rows(tibble(k = -1L, coef = 0, se = 0)) %>%
  arrange(k)

dir.create("output/tables",  recursive = TRUE, showWarnings = FALSE)
dir.create("output/figures", recursive = TRUE, showWarnings = FALSE)
write_csv(es_coefs, "output/tables/event_study_coefs.csv")

p_es <- ggplot(es_coefs, aes(k, coef)) +
  geom_hline(yintercept = 0, linewidth = 0.3) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "red") +
  geom_errorbar(aes(ymin = coef - 1.96 * se, ymax = coef + 1.96 * se),
                width = 0.2, color = "#1f3b73") +
  geom_point(color = "#1f3b73", size = 2) +
  labs(x = "Months relative to tariff implementation (Feb 2025)",
       y = expression(hat(beta)[k]),
       title = "Event study: dynamic effects of the 2025 tariff shock") +
  theme_minimal(base_size = 11)

ggsave("output/figures/fig1_event_study.png", p_es,
       width = 9, height = 5, dpi = 150)

did_tbl <- tibble(
  model    = c("DiD (TWFE) full", "DiD (TWFE) no Sec.232"),
  beta     = c(coef(did_full)["treat_intensity"],
               coef(did_no232)["treat_intensity"]),
  se_clust = c(se(did_full)["treat_intensity"],
               se(did_no232)["treat_intensity"]),
  p_clust  = c(pvalue(did_full)["treat_intensity"],
               pvalue(did_no232)["treat_intensity"]),
  N        = c(nobs(did_full), nobs(did_no232)),
  G        = c(18, 15)
)
write_csv(did_tbl, "output/tables/did_results.csv")
cat("\nDiD done. Wrote output/tables/did_results.csv\n")
