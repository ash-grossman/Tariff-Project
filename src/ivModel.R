# ==============================================================================
# ivModel.R
# ------------------------------------------------------------------------------
# Shift-share (Bartik-style) 2SLS for the 2025 tariff shock.
#
#   Endogenous:  tariff_shock_i * post_t
#   Instrument:  china_share_jan25_i * post_t
#      (pre-shock China import intensity predicts which industries were hit
#       hardest by Section 301 / reciprocal tariffs, but is plausibly
#       uncorrelated with post-Feb 2025 employment shocks orthogonal to policy.)
#
# Output: output/tables/iv_comparison.(csv|tex)
#         output/figures/fig3_coefficient_compare.png
# ==============================================================================

suppressPackageStartupMessages({
  library(tidyverse)
  library(fixest)
  library(modelsummary)
  library(ggplot2)
})

df <- read_csv("resources/processed/industry_panel_clean.csv", show_col_types = FALSE)

# ---- 1. Naive OLS (no fixed effects) ----------------------------------------
ols_naive <- feols(log_emp ~ treat_intensity, data = df, vcov = "HC1")

# ---- 2. TWFE DiD (repeated here for comparison) -----------------------------
did <- feols(log_emp ~ treat_intensity | industry + date,
             data = df, cluster = ~ industry)

# ---- 3. 2SLS with shift-share IV --------------------------------------------
iv_model <- feols(log_emp ~ 1 | industry + date |
                   treat_intensity ~ iv_china_post,
                 data    = df,
                 cluster = ~ industry)

# First-stage diagnostics
fs <- summary(iv_model, stage = 1)
print(fs)
F_first <- fitstat(iv_model, type = "ivf")[[1]]
cat("First-stage F =", round(F_first$stat, 3), "\n")

# ---- 4. 2SLS dropping Section 232 industries --------------------------------
sec232 <- c("Primary_Metal", "Fabricated_Metal", "Transportation_Equipment")
iv_no232 <- feols(log_emp ~ 1 | industry + date |
                    treat_intensity ~ iv_china_post,
                  data    = filter(df, !(industry %in% sec232)),
                  cluster = ~ industry)
F_no232 <- fitstat(iv_no232, type = "ivf")[[1]]

# ---- 5. Model-summary table -------------------------------------------------
modelsummary(
  list("(1) Naive OLS"          = ols_naive,
       "(2) TWFE DiD"           = did,
       "(3) 2SLS"               = iv_model,
       "(4) 2SLS (no Sec 232)"  = iv_no232),
  stars     = TRUE,
  gof_map   = c("nobs","r.squared"),
  coef_map  = c("treat_intensity"     = "Tariff Shock × Post",
                "fit_treat_intensity" = "Tariff Shock × Post"),
  output    = "output/tables/iv_comparison.tex"
)

# ---- 6. Coefficient comparison plot -----------------------------------------
extract_b <- function(model, name, is_iv = FALSE) {
  term <- if (is_iv) "fit_treat_intensity" else "treat_intensity"
  co <- coef(model)[term]
  se <- sqrt(diag(vcov(model)))[term]
  tibble(model = name, est = unname(co), se = unname(se))
}

plot_data <- bind_rows(
  extract_b(ols_naive, "Naive OLS"),
  extract_b(did,       "TWFE DiD"),
  extract_b(iv_model,  "2SLS",                is_iv = TRUE),
  extract_b(iv_no232,  "2SLS (excl. Sec 232)", is_iv = TRUE)
) %>% mutate(model = factor(model, levels = model))

p_cmp <- ggplot(plot_data, aes(model, est, color = model)) +
  geom_hline(yintercept = 0, linewidth = 0.3) +
  geom_pointrange(aes(ymin = est - 1.96*se, ymax = est + 1.96*se),
                  size = 0.8) +
  labs(x = NULL,
       y = "Coefficient on Tariff Shock × Post (log emp)",
       title = "Impact of 2025 tariff shock: bias-correction comparison") +
  theme_minimal(base_size = 11) +
  guides(color = "none") +
  theme(axis.text.x = element_text(angle = 15, hjust = 0.8))

ggsave("output/figures/fig3_coefficient_compare.png", p_cmp,
       width = 8, height = 5, dpi = 150)

cat("IV done.\n")
