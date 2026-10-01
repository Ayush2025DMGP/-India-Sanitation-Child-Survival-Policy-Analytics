# India Sanitation & Child Survival: Policy Analytics

## Research question
How did basic sanitation access and under-five mortality change in India, and how closely did they move together?

## Data and workflow
- Source: World Bank World Development Indicators public API.
- Geography/period: India, requested 2000–2022; API coverage may vary.
- Indicators: basic sanitation (% population; SH.STA.BASS.ZS) and under-five mortality (per 1,000 live births; SH.DYN.MORT).
- Steps: API retrieval, merge by year, type conversion, missingness review, EDA, descriptive statistics, charts, linear regression.

## Findings
- Sanitation: 21.1% in 2000 to 79.8% in 2022 (58.7 percentage points).
- Under-five mortality: 91.2 in 2000 to 29.9 in 2022 per 1,000 live births.
- Pearson correlation across 23 paired years: -0.97.

## Model
- In-sample descriptive regression
- Slope: -1.154; in-sample R²: 0.94; MAE: 2.8.

## Interpretation and limitations
- Correlation does not show that sanitation caused mortality changes.
- Income, nutrition, immunization, healthcare access, education, water quality, and measurement changes may affect both indicators.
- National annual averages hide state, district, rural/urban, and household inequalities.
- The regression is an introductory demonstration, not a causal evaluation or validated forecast.

## Policy-relevant next steps
1. Extend to state-level data where comparable observations exist.
2. Add contextual indicators such as drinking-water access, poverty, immunization, and health-service coverage.
3. Use a defensible evaluation design and comparison group for impact assessment.

## Reproducibility
Run `python analysis.py`; outputs are saved in `outputs/`.

## Source links
- https://data.worldbank.org/indicator/SH.STA.BASS.ZS?locations=IN
- https://data.worldbank.org/indicator/SH.DYN.MORT?locations=IN
- https://datahelpdesk.worldbank.org/knowledgebase/articles/889386-developer-information-overview
