# ==============================================================================
# run_all.R
# Reproduce the analysis end-to-end. Run from the project root.
# ==============================================================================
source("src/dataProcessor.R")
source("src/didModel.R")
source("src/ivModel.R")
source("src/robustness.R")
source("src/figures.R")
cat("\nDone. See output/figures and output/tables.\n")
