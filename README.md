# India Sanitation & Child Survival: Policy Analytics

A concise junior-analyst portfolio project using Python and public World Bank data.

**Research question:** How did basic sanitation access and under-five mortality change in India, and how closely did they move together?

## Skills demonstrated
- Public API data collection
- Pandas cleaning, type conversion, merging, and missing-value checks
- Exploratory data analysis and Matplotlib charts
- Descriptive statistics and Pearson correlation
- Scikit-learn linear regression, R², and MAE
- Automated Markdown policy brief and reproducible outputs

## Run
Python 3.9+ and internet access are required to retrieve the latest available data.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python analysis.py
```

The script creates `outputs/` with a cleaned CSV, two charts, JSON statistics/model results, and `policy_brief.md`.

## Indicators
- `SH.STA.BASS.ZS`: people using at least basic sanitation services (% of population)
- `SH.DYN.MORT`: under-five mortality rate (per 1,000 live births)

Source: World Bank World Development Indicators API. Exact available years can change as the source is updated.

## Important
This is descriptive observational analysis. A correlation or simple regression does not establish causality. National time series conceal regional and household differences; the report identifies these limitations and suggests extensions.
