# ==============================================================================
# figures.R
# ------------------------------------------------------------------------------
# Additional descriptive figures: employment trends by tariff-exposure tercile
# and the cross-industry scatter of tariff shock vs. employment change.
# ==============================================================================

suppressPackageStartupMessages({
  library(tidyverse)
  library(ggplot2)
  library(scales)
})

df <- read_csv("resources/processed/industry_panel_clean.csv", show_col_types = FALSE)

# ---- 1. Employment trends by tariff-exposure tercile ------------------------
shock <- df %>% distinct(industry, tariff_shock)
terciles <- quantile(shock$tariff_shock, c(1/3, 2/3), na.rm = TRUE)
shock <- shock %>%
  mutate(exposure = case_when(
    tariff_shock <= terciles[1] ~ "Low exposure",
    tariff_shock <= terciles[2] ~ "Mid exposure",
    TRUE                        ~ "High exposure"))

panel_t <- df %>%
  left_join(shock, by = c("industry","tariff_shock")) %>%
  group_by(exposure, date) %>%
  summarise(emp_index = mean(emp_thous / first(emp_thous[date == min(date)])),
            .groups = "drop") %>%
  group_by(exposure) %>%
  mutate(emp_index = emp_thous <- NULL,
         emp_index = emp_thous) %>%  # placeholder; replaced below
  ungroup()

# Cleaner computation
baseline <- df %>%
  filter(date == as.Date("2020-01-01")) %>%
  select(industry, emp_base = emp_thous)

trend <- df %>%
  left_join(baseline, by = "industry") %>%
  left_join(shock, by = c("industry","tariff_shock")) %>%
  group_by(exposure, date) %>%
  summarise(idx = mean(emp_thous / emp_base) * 100, .groups = "drop")

p_trend <- ggplot(trend, aes(date, idx, color = exposure)) +
  geom_vline(xintercept = as.Date("2025-02-01"),
             linetype = "dashed", color = "red") +
  annotate("text", x = as.Date("2025-03-15"), y = max(trend$idx, na.rm = TRUE),
           label = "Tariff\nFeb 2025", hjust = 0, color = "red", size = 3) +
  geom_line(linewidth = 0.8) +
  scale_color_manual(values = c("Low exposure" = "#6b9e2a",
                                "Mid exposure" = "#1f3b73",
                                "High exposure" = "#b02020")) +
  labs(x = NULL, y = "Employment index (Jan 2020 = 100)",
       color = NULL,
       title = "Manufacturing employment by tariff-exposure tercile") +
  theme_minimal(base_size = 11) +
  theme(legend.position = "bottom")

ggsave("output/figures/fig2_emp_trends.png", p_trend, width = 9, height = 5, dpi = 150)

# ---- 2. Scatter: tariff shock vs. change in log employment ------------------
pre  <- df %>% filter(between(date, as.Date("2024-01-01"), as.Date("2025-01-01"))) %>%
  group_by(industry) %>% summarise(pre  = mean(log_emp))
post <- df %>% filter(date >= as.Date("2025-02-01")) %>%
  group_by(industry) %>% summarise(post = mean(log_emp))
info <- df %>% distinct(industry, tariff_shock, china_share_jan25)

plot_df <- inner_join(pre, post, by = "industry") %>%
  inner_join(info, by = "industry") %>%
  mutate(dlog = (post - pre) * 100)

p_sc <- ggplot(plot_df, aes(tariff_shock * 100, dlog)) +
  geom_hline(yintercept = 0, color = "grey70") +
  geom_vline(xintercept = 0, color = "grey70") +
  geom_smooth(method = "lm", se = TRUE, color = "red", linetype = "dashed") +
  geom_point(aes(size = china_share_jan25),
             color = "#1f3b73", alpha = 0.8) +
  geom_text(aes(label = gsub("_", " ", industry)),
            size = 3, vjust = -1.3) +
  scale_size_continuous(range = c(2, 7)) +
  labs(x = "Tariff shock (pp)", y = expression(Delta~"log employment "~("%")),
       size = "China share (Jan '25)",
       title = "Cross-industry: tariff shock vs. employment change") +
  theme_minimal(base_size = 11)

ggsave("output/figures/fig4_scatter.png", p_sc, width = 9, height = 6, dpi = 150)
cat("Figures done.\n")
