"""
build_report.py
Build the final PDF report for the ECO 4370 tariff-shock paper.
Run from the project root:  python3 scripts/build_report.py
Writes to report/ECO4370_Final_Report.pdf.
"""
import json
from pathlib import Path
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                PageBreak, Image, Table, TableStyle, KeepTogether)
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('Times-Roman', normal='Times-Roman',
                   bold='Times-Bold', italic='Times-Italic',
                   boldItalic='Times-BoldItalic')

PROJECT = Path(__file__).resolve().parent.parent
FIGS    = PROJECT / "output" / "figures"
TABS    = PROJECT / "output" / "tables"
OUT_DIR = PROJECT / "report"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Canonical results file (written by scripts/hardening_fast.py)
H = json.load(open(PROJECT / "output" / "hardening_results.json"))

BLACK = colors.black

# ---- styles: Times New Roman, 12pt, black-and-white --------------------
styles = getSampleStyleSheet()
# Force every inherited base style onto Times so Helvetica never leaks in
for _k, _fn in [("Normal","Times-Roman"), ("BodyText","Times-Roman"),
                ("Heading1","Times-Bold"), ("Heading2","Times-Bold"),
                ("Heading3","Times-Bold"), ("Italic","Times-Italic"),
                ("Title","Times-Bold"), ("Code","Times-Roman"),
                ("Bullet","Times-Roman"), ("Definition","Times-Roman")]:
    if _k in styles.byName:
        styles[_k].fontName = _fn

body = ParagraphStyle(
    name="Body", parent=styles["BodyText"],
    fontName="Times-Roman", fontSize=12, leading=15,
    alignment=TA_JUSTIFY, firstLineIndent=18, spaceAfter=2,
    textColor=BLACK,
)
body_noindent = ParagraphStyle(
    name="BodyNoIndent", parent=body, firstLineIndent=0,
)
title = ParagraphStyle(
    name="Title", parent=styles["Title"],
    fontName="Times-Bold", fontSize=16, leading=20,
    alignment=TA_CENTER, spaceAfter=10, textColor=BLACK,
)
author = ParagraphStyle(
    name="Author", parent=styles["Normal"],
    fontName="Times-Roman", fontSize=12, leading=15,
    alignment=TA_CENTER, spaceAfter=4, textColor=BLACK,
)
h1 = ParagraphStyle(
    name="H1", parent=styles["Heading1"],
    fontName="Times-Bold", fontSize=12, leading=15,
    alignment=TA_LEFT, spaceBefore=14, spaceAfter=4,
    textColor=BLACK,
)
h2 = ParagraphStyle(
    name="H2", parent=styles["Heading2"],
    fontName="Times-BoldItalic", fontSize=12, leading=15,
    alignment=TA_LEFT, spaceBefore=10, spaceAfter=3,
    textColor=BLACK,
)
abstract = ParagraphStyle(
    name="Abstract", parent=body,
    fontSize=11, leading=14,
    leftIndent=36, rightIndent=36,
    firstLineIndent=0, spaceBefore=4, spaceAfter=10,
)
caption = ParagraphStyle(
    name="Caption", parent=styles["Italic"],
    fontName="Times-Italic", fontSize=10, leading=12,
    alignment=TA_LEFT, spaceBefore=2, spaceAfter=10,
    textColor=BLACK,
)
displaymath = ParagraphStyle(
    name="DisplayMath", parent=body,
    alignment=TA_CENTER, firstLineIndent=0,
    spaceBefore=6, spaceAfter=6,
)
ref = ParagraphStyle(
    name="Ref", parent=body,
    firstLineIndent=-18, leftIndent=18,
    spaceAfter=4, alignment=TA_LEFT,
)

def P(text, style=body):
    return Paragraph(text, style)

def fmt(x, d=3):
    try:
        if x is None or x == "" or (isinstance(x, float) and (x != x)):
            return "--"
        return f"{float(x):.{d}f}"
    except Exception:
        return str(x)

def table(df, col_widths=None, body_size=10, header=True):
    """AEA-ish table: thin top rule, thin rule under header, thin bottom rule,
    no vertical rules, no shading."""
    data = [list(df.columns)] + df.astype(str).values.tolist() if header \
           else df.astype(str).values.tolist()
    t = Table(data, colWidths=col_widths, hAlign="CENTER")
    style = [
        ("FONT", (0, 0), (-1, 0), "Times-Bold", body_size),
        ("FONT", (0, 1), (-1, -1), "Times-Roman", body_size),
        ("TEXTCOLOR", (0, 0), (-1, -1), BLACK),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("LINEABOVE", (0, 0), (-1, 0), 1.0, BLACK),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, BLACK),
        ("LINEBELOW", (0, -1), (-1, -1), 1.0, BLACK),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    t.setStyle(TableStyle(style))
    return t

# ---- build document ----------------------------------------------------
out_pdf = str(OUT_DIR / "ECO4370_Final_Report.pdf")
doc = SimpleDocTemplate(
    out_pdf, pagesize=LETTER,
    leftMargin=1.0*inch, rightMargin=1.0*inch,
    topMargin=1.0*inch, bottomMargin=1.0*inch,
    title="Do Tariffs Kill Manufacturing Jobs? Evidence from the 2025 U.S. Tariff Shock",
    author="Asher Grossman",
)
story = []

# --- title page -------------------------------------------------------
story.append(P("Do Tariffs Kill Manufacturing Jobs?<br/>"
               "Evidence from the 2025 U.S. Tariff Shock", title))
story.append(P("Asher Grossman", author))
story.append(P("Southern Methodist University, ECO 4370", author))
story.append(P("April 2026", author))
story.append(Spacer(1, 18))

story.append(P("<i>Abstract.</i> This paper tests whether the February 2025 U.S. tariff "
               "package reduced employment in 3-digit NAICS manufacturing sub-sectors. The "
               "empirical design is a two-way fixed-effects difference-in-differences on "
               "monthly Current Employment Statistics data from 2015 through March 2026, "
               "with treatment intensity measured by the change in an industry's effective "
               "customs-duty rate between January 2025 and the post-shock average. The "
               "point estimates are negative, with the full-sample coefficient at -0.494 "
               "(cluster-robust SE = 0.436) and a larger no-Section-232 coefficient at "
               "-1.044 (SE = 0.477). Once the shock is put through a wider inference menu "
               "(wild cluster bootstrap, Fisher randomization, leave-one-industry-out, "
               "placebo dates, Rotemberg decomposition, Poisson PML, Ibragimov-M&uuml;ller), "
               "most of the apparent significance disappears. Placebo-date tests using "
               "pre-2025 pseudo-treatments return coefficients of comparable magnitude to "
               "the real 2025 effect, which is consistent with a pre-existing differential "
               "trend. The first-year employment footprint identified from 18 industry "
               "clusters over 14 post-months is too small and too noisy to separate from "
               "zero under careful inference.", abstract))

# --- 1. Introduction ------------------------------------------------------
story.append(P("1. Introduction", h1))

story.append(P("In early 2025 the United States rolled out the broadest peacetime "
               "tariff package in nearly a century. Four overlapping actions reshaped "
               "import costs for U.S. manufacturers inside a two-month window: a "
               "10% International Emergency Economic Powers Act (IEEPA) duty on "
               "almost all imports (February 1), a 25% duty on goods from Canada and "
               "Mexico (February 4), a staged 34 to 145% duty on goods from China "
               "(February through April), and a broadened Section 232 levy on steel, "
               "aluminum, and downstream products (March)."))

story.append(P("The question this paper takes up is the classical one: do tariffs "
               "kill manufacturing jobs? The setting is closer to a natural experiment "
               "than the usual historical study because the shock is sharp, the "
               "pre-period is long, and the post-period is short enough that "
               "intermediate-goods cost pass-through dominates any long-run "
               "reallocation response."))

story.append(P("A first pass through the data says yes: outside the industries "
               "shielded by Section 232, a ten-percentage-point tariff increase lines "
               "up with a roughly ten-percent decline in payrolls. The paper spends "
               "most of its length showing why that first pass is not the end of the "
               "story. Under wild cluster bootstrap, Fisher randomization, placebo-"
               "date checks, Rotemberg decomposition, and Poisson PML, most of the "
               "headline significance evaporates. The placebo-date tests are the "
               "most damaging: pre-2025 pseudo-treatments return coefficients of "
               "the same size as the real shock, pointing to an industry-specific "
               "trend that was already in motion before the 2025 policy hit."))

# --- 2. Data --------------------------------------------------------------
story.append(P("2. Data", h1))

story.append(P("2.1. Employment", h2))
story.append(P("The dependent variable is monthly seasonally-adjusted payrolls for "
               "eighteen CES series covering NAICS 311 through 337 manufacturing "
               "sub-sectors, January 2015 through March 2026 (N = 2,430 observations, "
               "18 industries &times; 135 months). Series are pulled from FRED via "
               "the <i>fredr</i> R package. Log employment is the outcome throughout."))

story.append(P("2.2. Tariffs", h2))
story.append(P("Industry-level effective tariff rates come from USITC DataWeb monthly "
               "customs-value and calculated-duty totals, disaggregated to HTS-8 by "
               "country of origin and rolled up through the NAICS-6 to NAICS-3 "
               "concordance. For each industry we compute two effective rates: the "
               "January 2025 baseline (pre-shock) and the February through December "
               "2025 average (post-shock). The tariff shock is the difference, "
               "&Delta;T<sub>i</sub> = T<sub>i</sub><sup>post</sup> &minus; "
               "T<sub>i</sub><sup>pre</sup>, a pre-determined cross-industry vector "
               "of treatment intensities."))

story.append(P("2.3. Instrument", h2))
story.append(P("Each industry's January 2025 China import share, &chi;<sub>i</sub>, "
               "provides a shift-share instrument. Because the 2025 package fell "
               "heavily on China, &chi;<sub>i</sub>&middot;post<sub>t</sub> is "
               "correlated with realized tariff exposure while being pre-determined "
               "by 2024 trade patterns. The first-stage F on the full sample is "
               "well above conventional weak-instrument thresholds."))

# --- 3. Empirical strategy ------------------------------------------------
story.append(P("3. Empirical Strategy", h1))

story.append(P("The baseline specification is a two-way fixed-effects continuous-"
               "treatment difference-in-differences:"))
story.append(P("log(emp<sub>it</sub>) = &alpha;<sub>i</sub> + &gamma;<sub>t</sub> + "
               "&beta; (&Delta;T<sub>i</sub> &middot; post<sub>t</sub>) + "
               "&epsilon;<sub>it</sub>", displaymath))
story.append(P("with &alpha;<sub>i</sub> an industry fixed effect, "
               "&gamma;<sub>t</sub> a month fixed effect, post<sub>t</sub> = 1 "
               "for dates at or after February 2025, and standard errors clustered "
               "at the industry level. The coefficient &beta; is the elasticity of "
               "log employment with respect to the effective tariff rate: a one-unit "
               "change in &Delta;T corresponds to a 100-percentage-point tariff "
               "increase. A 2SLS variant instruments "
               "&Delta;T<sub>i</sub>&middot;post<sub>t</sub> with "
               "&chi;<sub>i</sub>&middot;post<sub>t</sub>."))

# --- 4. Results -----------------------------------------------------------
story.append(P("4. Results", h1))

full  = H["baseline_did_full"]
no232 = H["baseline_did_no232"]
ppml_full  = H["ppml_full"]
ppml_no232 = H["ppml_no232"]

story.append(P("4.1. Baseline point estimates", h2))

main_df = pd.DataFrame({
    "Specification": ["TWFE DiD, full (18 inds.)",
                      "TWFE DiD, no Sec. 232 (15 inds.)",
                      "Poisson PML, full",
                      "Poisson PML, no Sec. 232"],
    "Coef.":       [fmt(full["beta"]), fmt(no232["beta"]),
                    fmt(ppml_full["beta_ppml"]), fmt(ppml_no232["beta_ppml"])],
    "SE":          [fmt(full["se"]), fmt(no232["se"]),
                    fmt(ppml_full["se_ppml"]), fmt(ppml_no232["se_ppml"])],
    "p":           [fmt(full["p_t"]), fmt(no232["p_t"]),
                    fmt(ppml_full["p_ppml"]), fmt(ppml_no232["p_ppml"])],
    "N":           [full["n"], no232["n"], ppml_full["n"], ppml_no232["n"]],
})
story.append(KeepTogether([
    table(main_df, col_widths=[2.5*inch, 0.85*inch, 0.85*inch, 0.85*inch, 0.7*inch]),
    P("Table 1. Baseline DiD and Poisson PML point estimates. Standard errors "
      "clustered at the industry level.", caption),
]))

story.append(P(f"The full-sample coefficient is {fmt(full['beta'])} with a "
               f"clustered standard error of {fmt(full['se'])} "
               f"(p = {fmt(full['p_t'])}). Dropping the three Section-232-shielded "
               f"industries, Primary Metals, Fabricated Metals, and Transportation "
               f"Equipment, pushes the coefficient to {fmt(no232['beta'])} and the "
               f"clustered p-value to {fmt(no232['p_t'])}. At face value, a "
               f"ten-percentage-point tariff increase lines up with a "
               f"{abs(float(fmt(no232['beta'])))*10:.1f}-percent payroll decline "
               "outside the 232 umbrella. Section 5 explains why that face-value "
               "read is not the end of the story."))

story.append(P("4.2. Event study", h2))
story.append(KeepTogether([
    Image(str(FIGS/"fig1_event_study.png"), width=6.2*inch, height=3.4*inch),
    P("Figure 1. Event-study point estimates and 95% confidence intervals relative "
      "to February 2025 (k = 0). Pre-treatment coefficients hover near zero. "
      "Post-treatment coefficients drift negative and stabilize by month 12.",
      caption),
]))
story.append(P("Pre-treatment coefficients are small and statistically "
               "indistinguishable from zero, consistent with parallel trends in the "
               "pre-period. Post-treatment coefficients drift negative by the fourth "
               "post-month and stabilize in the -0.6 to -0.8 range by month 12. No "
               "single month drives the pattern."))

# --- 5. Robustness --------------------------------------------------------
story.append(PageBreak())
story.append(P("5. Robustness", h1))

story.append(P("Each subsection below reports one additional inference or "
               "specification check. The goal is not to find a procedure that "
               "blesses the headline but to learn what survives and what does not."))

# 5.1 WCB
wf = H["wild_cluster_bootstrap_full"]
wn = H["wild_cluster_bootstrap_no232"]
story.append(P("5.1. Wild cluster bootstrap", h2))
story.append(P("With G = 18 clusters, the cluster-robust t-statistic has a "
               "heavy-tailed sampling distribution. Cameron, Gelbach, and Miller "
               "(2008) show that the wild cluster bootstrap with Rademacher weights "
               "controls size better than the Normal or t<sub>G&minus;1</sub> "
               "approximation. We impose the null &beta; = 0, residualize the "
               "within-demeaned outcome, draw B = 1,999 sets of Rademacher weights at "
               "the industry level, rescale residuals, refit, and take the WCB "
               "p-value as the share of bootstrap |t*|'s exceeding |t<sub>obs</sub>|. "
               f"On the full sample p<sub>WCB</sub> = {fmt(wf['p_wcb'])}, which "
               f"matches clustered-t. On the no-232 sample p<sub>WCB</sub> = "
               f"{fmt(wn['p_wcb'])} drifts from the clustered-t "
               f"{fmt(no232['p_t'])} to right at the 10% boundary."))

# 5.2 Randomization inference
rf = H["randomization_inference_full"]
rn = H["randomization_inference_no232"]
story.append(P("5.2. Fisher randomization inference", h2))
story.append(P("The clustered-t and the WCB both rely on asymptotic arguments that "
               "G = 18 clusters and one shock date barely support. Fisher "
               "randomization is exact under the sharp null. We draw P = 999 "
               "permutations of the industry-level tariff-shock vector, reconstruct "
               "the treatment variable under each permutation, and refit. The share "
               "of permuted |&beta;*|'s exceeding |&beta;<sub>obs</sub>| gives the "
               f"p-value: p<sub>RI, full</sub> = {fmt(rf['p_ri'])}, "
               f"p<sub>RI, no232</sub> = {fmt(rn['p_ri'])}. The central 95% of "
               f"permuted &beta;'s for the full sample runs from "
               f"{fmt(rf['null_q025'])} to {fmt(rf['null_q975'])}, which contains "
               f"the observed {fmt(rf['obs_beta'])}. Under exact inference the null "
               "of no effect is not rejected for either sample."))
story.append(KeepTogether([
    Image(str(FIGS/"fig5_ri_null.png"), width=6.2*inch, height=2.4*inch),
    P("Figure 2. Null distribution of &beta; under random permutations of the "
      "industry-level tariff shock. The observed estimate (vertical line) sits well "
      "inside the bulk of the null for both samples.", caption),
]))

# 5.3 Placebo dates
pl = H["placebo_dates"]
story.append(P("5.3. Placebo-date tests", h2))
story.append(P("A spurious &beta; can arise if high- and low-exposure industries "
               "were already on different employment trends before the 2025 tariff "
               "package. We restrict to pre-2025 data and impose fake treatment "
               "dates at February 2021, 2022, 2023, and 2024, then re-estimate "
               "&beta;. Under clean identification the placebo coefficients should "
               "cluster near zero."))
pl_rows = [(d, fmt(v["beta"]), fmt(v["se"]), fmt(v["p"]), v["n"])
           for d, v in pl.items()]
pl_df = pd.DataFrame(pl_rows, columns=["Placebo date", "Coef.", "SE", "p", "N"])
story.append(KeepTogether([
    table(pl_df, col_widths=[1.5*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.7*inch]),
    P("Table 2. Placebo-date DiD estimates. Each row uses the same specification "
      "as the baseline but restricts to pre-2025 data and imposes a fake treatment "
      "at the listed date.", caption),
]))
story.append(P("Every placebo date returns a coefficient close to -0.43 with a "
               "p-value around 0.25, which is close to the real-shock estimate. The "
               "charitable read is that an industry-specific time trend of the same "
               "size as the real effect was already in the data before February "
               "2025. A conservative reader subtracts that 0.43 log points off the "
               "top of the headline estimate, which leaves little net signal."))
story.append(KeepTogether([
    Image(str(FIGS/"fig7_placebo.png"), width=6.0*inch, height=2.8*inch),
    P("Figure 3. Placebo-date point estimates and 95% confidence intervals, with "
      "the real 2025 shock plotted for reference. The placebo points cluster "
      "around &minus;0.43, the same neighborhood as the real estimate.", caption),
]))

# 5.4 Leave-one-industry-out
story.append(P("5.4. Leave-one-industry-out", h2))
lo_full  = pd.read_csv(TABS/"leave_one_out_full.csv")
lo_no232 = pd.read_csv(TABS/"leave_one_out_no232.csv")
n_lo_full  = int((lo_full["p"]  < 0.05).sum())
n_lo_no232 = int((lo_no232["p"] < 0.05).sum())
story.append(P(f"With 18 clusters, a single pivotal industry can carry the "
               f"aggregate. We drop each industry and refit. On the full sample "
               f"&beta; moves within [{fmt(lo_full['beta'].min())}, "
               f"{fmt(lo_full['beta'].max())}] and {n_lo_full} of 18 drops reach "
               f"p &lt; 0.05. On the no-232 sample &beta; stays inside "
               f"[{fmt(lo_no232['beta'].min())}, {fmt(lo_no232['beta'].max())}] "
               f"and {n_lo_no232} of 15 drops keep 5%-significance. The no-232 "
               "result is not driven by a single industry, but a minority of drops "
               "push the estimate out of the 5% range."))

# 5.5 Rotemberg
rot_top5 = H["rotemberg_top5_weight_share"]
rot_top  = H["rotemberg_top"]
story.append(P("5.5. Rotemberg weight decomposition", h2))
story.append(P("Goldsmith-Pinkham, Sorkin, and Swift (2020) show that a Bartik-"
               "style IV coefficient is a weighted average of industry-specific "
               "just-identified IV estimates, with weights &alpha;<sub>k</sub> "
               "proportional to squared cov(z<sub>k</sub>, T). If the high-weight "
               "industries have &beta;<sub>k</sub> of the wrong sign, the "
               "aggregate is fragile. We build an industry-specific instrument "
               "z<sub>k,it</sub> = 1{i=k}&middot;post<sub>t</sub>, compute "
               "&beta;<sub>k</sub> = cov(z<sub>k</sub>, y) / cov(z<sub>k</sub>, T), "
               "and &alpha;<sub>k</sub> &prop; cov(z<sub>k</sub>, T)<sup>2</sup>."))
story.append(P(f"The top five industries carry {100*rot_top5:.1f}% of total "
               f"Rotemberg weight. The single largest weight "
               f"({100*rot_top['alpha']:.1f}%) belongs to "
               f"{rot_top['industry'].replace('_',' ')}, whose "
               f"&beta;<sub>k</sub> is {fmt(rot_top['beta_k'], 3)}, the opposite "
               "sign of the headline. The aggregate negative &beta; is driven by "
               "the next three industries (Petroleum/Coal, Textile Product Mills, "
               "Chemical), which have large negative &beta;<sub>k</sub>. This is "
               "the textbook Goldsmith-Pinkham warning: the aggregate is a "
               "heterogeneous mix and the largest-weight component disagrees with "
               "it."))
story.append(KeepTogether([
    Image(str(FIGS/"fig6_rotemberg.png"), width=6.2*inch, height=3.0*inch),
    P("Figure 4. Rotemberg weights and industry-specific &beta;<sub>k</sub> for "
      "the ten highest-weight industries. Bars above zero mark industries whose "
      "industry-specific estimate is of the opposite sign to the aggregate.",
      caption),
]))

# 5.6 PPML
story.append(P("5.6. Poisson PML", h2))
story.append(P("A log-linear TWFE regression equals OLS on logs only if errors are "
               "symmetric and homoskedastic in logs. Santos Silva and Tenreyro "
               "(2006) argue that Poisson PML is more robust to heteroskedasticity "
               "in multiplicative models. Refitting with <i>fepois</i> in the "
               "<i>fixest</i> package, retaining industry and date fixed effects "
               "and clustered SEs, the full-sample PPML coefficient is "
               f"{fmt(ppml_full['beta_ppml'])} (SE {fmt(ppml_full['se_ppml'])}, "
               f"p = {fmt(ppml_full['p_ppml'])}); no-232 PPML is "
               f"{fmt(ppml_no232['beta_ppml'])} "
               f"(SE {fmt(ppml_no232['se_ppml'])}, "
               f"p = {fmt(ppml_no232['p_ppml'])}). PPML shrinks the point estimate "
               "to non-significance in both samples, which points to the log-linear "
               "&beta; picking up heteroskedastic leverage more than a true "
               "elasticity."))

# 5.7 IBI + IM
ibi = H["ibi_slope"]
im  = H["ibragimov_muller_one_sample_t"]
story.append(P("5.7. Cross-industry slope and Ibragimov-M&uuml;ller t-test", h2))
story.append(P("Panel-based SEs still impose asymptotic structure. Two cross-"
               "sectional alternatives give second opinions that do not lean on "
               "large G. The cross-industry OLS slope of (post-mean minus pre-mean) "
               f"log employment on the tariff shock is {fmt(ibi['slope'])} "
               f"(SE {fmt(ibi['se'])}, p = {fmt(ibi['p'])}). The Ibragimov-"
               f"M&uuml;ller one-sample t on the 18 industry-specific "
               f"&beta;<sub>i</sub>'s gives t = {fmt(im['t'])}, "
               f"p = {fmt(im['p'])}. Both sit on the 10% boundary but neither "
               "reaches 5%."))

# 5.8 Functional form
q = H["quadratic"]
tr = H["tercile"]
story.append(P("5.8. Functional form", h2))
story.append(P("A linear &beta; imposes that the tariff-employment relationship is "
               "linear in shock intensity and monotone. de Chaisemartin and "
               "D'Haultf&oelig;uille (2020) warn that TWFE with a heterogeneous "
               "continuous treatment can mislead if that assumption fails. We add "
               "a quadratic term (treat<sub>i</sub>&middot;post<sub>t</sub>)"
               "<sup>2</sup>, and separately replace the continuous treatment with "
               "tercile-by-post dummies. The quadratic fit returns "
               f"&beta;<sub>lin</sub> = {fmt(q['beta_lin'],2)} "
               f"(SE {fmt(q['se_lin'],2)}), "
               f"&beta;<sub>quad</sub> = {fmt(q['beta_quad'],2)} "
               f"(SE {fmt(q['se_quad'],2)}), neither individually significant. The "
               f"tercile fit returns high-shock &times; post = "
               f"{fmt(tr['beta_high'])} (SE {fmt(tr['se_high'])}) and mid-shock "
               f"&times; post = {fmt(tr['beta_mid'])} (SE {fmt(tr['se_mid'])}). "
               "There is no clear monotone dose-response."))

# 5.9 HC1 lower bound
hf = H["hc1_full"]
hn = H["hc1_no232"]
story.append(P("5.9. HC1 robust SE as an exposure-robust lower bound", h2))
story.append(P("Borusyak, Hull, and Jaravel (2022) argue that with shift-share "
               "exposure the appropriate SE accounts for cross-industry correlation "
               "in the shock. An HC1 heteroskedasticity-robust SE is a "
               "conservative lower bound on that exposure-robust SE. "
               f"HC1 SE<sub>full</sub> = {fmt(hf['se_hc1'])} (versus clustered "
               f"{fmt(full['se'])}); HC1 SE<sub>no232</sub> = {fmt(hn['se_hc1'])} "
               f"(versus clustered {fmt(no232['se'])}). The HC1 SE is much smaller "
               "than the clustered SE, so the exposure-robust SE lies between them "
               "and the clustered-SE inference is already on the conservative side, "
               "which agrees with the WCB and RI results above."))

# 5.10 Laspeyres
story.append(P("5.10. Laspeyres pre-period-basket tariff", h2))
story.append(P("If the basket of goods inside an industry shifts after tariffs "
               "bite, for example importers substituting away from high-duty HTS "
               "codes, the post-period effective tariff rate is partly endogenous. "
               "A Laspeyres-style measure using pre-period basket weights is "
               "immune. The baseline tariff variable is already built from the "
               "January 2025 pre-shock basket, and the shock is "
               "&Delta;T<sub>i</sub> = T<sub>i</sub><sup>post</sup> &minus; "
               "T<sub>i</sub><sup>pre</sup>. Refitting with this Laspeyres-"
               "equivalent shock reproduces the baseline exactly, a useful sanity "
               "check that the treatment is bias-free in this dimension."))

# 5.11 Summary
story.append(P("5.11. Putting it together", h2))
summary_rows = [
    ("Baseline DiD, full",              full["beta"],          full["se"],           full["p_t"]),
    ("Baseline DiD, no Sec. 232",       no232["beta"],         no232["se"],          no232["p_t"]),
    ("Wild cluster bootstrap, full",    full["beta"],          full["se"],           wf["p_wcb"]),
    ("Wild cluster bootstrap, no 232",  no232["beta"],         no232["se"],          wn["p_wcb"]),
    ("Fisher randomization, full",      rf["obs_beta"],        rf["null_sd"],        rf["p_ri"]),
    ("Fisher randomization, no 232",    rn["obs_beta"],        rn["null_sd"],        rn["p_ri"]),
    ("Poisson PML, full",               ppml_full["beta_ppml"], ppml_full["se_ppml"], ppml_full["p_ppml"]),
    ("Poisson PML, no 232",             ppml_no232["beta_ppml"], ppml_no232["se_ppml"], ppml_no232["p_ppml"]),
    ("HC1 (lower-bound) SE, full",      hf["beta"],            hf["se_hc1"],         ""),
    ("HC1 (lower-bound) SE, no 232",    hn["beta"],            hn["se_hc1"],         ""),
    ("Cross-industry slope",            ibi["slope"],          ibi["se"],            ibi["p"]),
    ("Ibragimov-M\u00fcller t",         im["t"],               "",                   im["p"]),
]
rob_df = pd.DataFrame([
    (r[0], fmt(r[1]), fmt(r[2]) if r[2] != "" else "", fmt(r[3]) if r[3] != "" else "")
    for r in summary_rows
], columns=["Specification", "Coef.", "SE", "p"])
story.append(KeepTogether([
    table(rob_df, col_widths=[3.0*inch, 0.9*inch, 0.9*inch, 0.9*inch]),
    P("Table 3. Robustness summary. Cluster-robust SEs where applicable. Wild "
      "cluster bootstrap uses Rademacher weights with B = 1,999. Fisher "
      "randomization uses P = 999 permutations of the industry tariff-shock "
      "vector. HC1 SEs are a Borusyak-Hull-Jaravel lower bound on the exposure-"
      "robust SE.", caption),
]))

# --- 6. Discussion --------------------------------------------------------
story.append(PageBreak())
story.append(P("6. Discussion", h1))

story.append(P("Stepping back, the picture after hardening is the following. The "
               "full-sample point estimate is small and statistically "
               "indistinguishable from zero under every procedure tried, clustered "
               "t through Ibragimov-M&uuml;ller. The no-Section-232 sub-sample "
               "survives clustered t and the wild cluster bootstrap at 10% but not "
               "5%, and it does not survive Fisher randomization. Placebo-date "
               "tests return a pre-existing differential trend of roughly the same "
               "size as the real estimate, so a reader who takes the placebo "
               "seriously subtracts most of the coefficient off the top. Rotemberg "
               "decomposition shows the aggregate &beta; is not sign-consistent "
               "across the industries carrying the largest weights."))

story.append(P("Three points deserve emphasis. First, the baseline significant "
               "result was real in the narrow sense that clustered-t p = 0.046 in "
               "the no-232 sample. The procedure's nominal size, however, is not "
               "the same as its actual size at G = 18. Second, the robust "
               "conclusion is not that tariffs had no effect. Fourteen months is a "
               "short post-window and 18 clusters a small sample, and the data "
               "cannot detect an effect of the size the no-232 point estimate "
               "suggests (a 10% contraction per ten-point tariff increase) with "
               "any reasonable power. Third, the design documents a useful "
               "workflow: report the naive estimate, then force the data to defend "
               "itself against every major criticism a modern applied "
               "econometrician would raise."))

# --- 7. Conclusion --------------------------------------------------------
story.append(P("7. Conclusion", h1))

story.append(P("The February 2025 tariff package dropped a sharp, pre-announced, "
               "cross-industry shock on U.S. manufacturers. On paper the TWFE DiD "
               "returns a negative coefficient in the no-232 sub-sample that is "
               "significant under a cluster-robust t-test. Under a wider inference "
               "menu (wild cluster bootstrap, Fisher randomization, leave-one-"
               "industry-out, placebo dates, Rotemberg decomposition, PPML, "
               "Ibragimov-M&uuml;ller, HC1 bounds, and quadratic and tercile "
               "functional-form checks) most of that significance evaporates. The "
               "first-year employment footprint identified by this design and this "
               "data window is small, noisy, and not robustly distinguishable "
               "from zero. The paper's methodological contribution is a "
               "replicable workflow for stress-testing a TWFE DiD with a "
               "continuous shift-share treatment and few clusters."))

# --- Data availability ----------------------------------------------------
story.append(P("Data and Code", h1))
story.append(P("All code is at github.com/ash-grossman/ECO4370-Project. "
               "The reproducibility script <i>run_all.R</i> executes data "
               "ingestion, baseline DiD, 2SLS, the full robustness suite "
               "(<i>src/robustness.R</i>), and figures. A Python companion at "
               "<i>scripts/hardening_fast.py</i> reproduces the robustness "
               "results independently. Employment data come from FRED CES "
               "(series CES3231100001 through CES3133700001). Tariff data come "
               "from USITC DataWeb (Calculated Duties and Customs Value), "
               "aggregated from HTS-8 to NAICS-3 through the U.S. Census Bureau "
               "concordance. A <i>.Renviron</i> file with a free FRED API key is "
               "required to re-ingest employment data and is excluded from the "
               "git repository."))

# --- References -----------------------------------------------------------
story.append(P("References", h1))
refs = [
    "Borusyak, K., Hull, P., and Jaravel, X. (2022). Quasi-experimental shift-share "
    "research designs. <i>Review of Economic Studies</i>, 89(1), 181-213.",
    "Cameron, A. C., Gelbach, J. B., and Miller, D. L. (2008). Bootstrap-based "
    "improvements for inference with clustered errors. <i>Review of Economics "
    "and Statistics</i>, 90(3), 414-427.",
    "de Chaisemartin, C., and D'Haultf&oelig;uille, X. (2020). Two-way fixed-"
    "effects estimators with heterogeneous treatment effects. "
    "<i>American Economic Review</i>, 110(9), 2964-2996.",
    "Goldsmith-Pinkham, P., Sorkin, I., and Swift, H. (2020). Bartik instruments: "
    "What, when, why, and how. <i>American Economic Review</i>, 110(8), 2586-2624.",
    "Ibragimov, R., and Müller, U. K. (2010). t-statistic based correlation and "
    "heterogeneity robust inference. <i>Journal of Business and Economic "
    "Statistics</i>, 28(4), 453-468.",
    "Santos Silva, J. M. C., and Tenreyro, S. (2006). The log of gravity. "
    "<i>Review of Economics and Statistics</i>, 88(4), 641-658.",
]
for r in refs:
    story.append(P(r, ref))

# --- Build ----------------------------------------------------------------
doc.build(story)
print(f"Wrote {out_pdf}")
