"""India sanitation and child survival: beginner-friendly policy analytics.
Downloads World Bank WDI data, cleans, explores, models, and writes outputs.
Descriptive analysis only; it does not establish causality.
"""
from pathlib import Path
import json

import requests
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

START, END, COUNTRY = 2000, 2022, "IND"
OUT = Path("outputs")
OUT.mkdir(exist_ok=True)
INDICATORS = {
    "SH.STA.BASS.ZS": "basic_sanitation_pct",
    "SH.DYN.MORT": "under5_mortality_per_1000",
}


def fetch_indicator(code):
    url = (
        f"https://api.worldbank.org/v2/country/{COUNTRY}/indicator/{code}"
        f"?date={START}:{END}&format=json&per_page=200"
    )
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
        raise RuntimeError(f"No observations returned for {code}")
    return pd.DataFrame(
        [
            {"year": int(x["date"]), "value": x["value"]}
            for x in payload[1]
            if x.get("date") and x.get("value") is not None
        ]
    )


def get_data():
    frames = []
    for code, name in INDICATORS.items():
        frames.append(fetch_indicator(code).rename(columns={"value": name}))
    df = frames[0].merge(frames[1], on="year", how="outer")
    for col in INDICATORS.values():
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return (
        df.dropna(subset=["year"])
        .assign(year=lambda x: x.year.astype(int))
        .query("@START <= year <= @END")
        .sort_values("year")
        .drop_duplicates("year")
        .reset_index(drop=True)
    )


def analyze(df):
    paired = df.dropna(subset=list(INDICATORS.values()))
    s = df.dropna(subset=["basic_sanitation_pct"])
    m = df.dropna(subset=["under5_mortality_per_1000"])
    stats = {
        "country": "India",
        "period_requested": f"{START}-{END}",
        "rows": int(len(df)),
        "paired_years": int(len(paired)),
        "missing_values": {c: int(df[c].isna().sum()) for c in INDICATORS.values()},
    }
    if len(s) >= 2:
        stats.update(
            sanitation_start_year=int(s.iloc[0].year),
            sanitation_start_pct=round(float(s.iloc[0].basic_sanitation_pct), 2),
            sanitation_end_year=int(s.iloc[-1].year),
            sanitation_end_pct=round(float(s.iloc[-1].basic_sanitation_pct), 2),
            sanitation_change_percentage_points=round(
                float(s.iloc[-1].basic_sanitation_pct - s.iloc[0].basic_sanitation_pct), 2
            ),
        )
    if len(m) >= 2:
        stats.update(
            mortality_start_year=int(m.iloc[0].year),
            mortality_start_rate=round(float(m.iloc[0].under5_mortality_per_1000), 2),
            mortality_end_year=int(m.iloc[-1].year),
            mortality_end_rate=round(float(m.iloc[-1].under5_mortality_per_1000), 2),
            mortality_change=round(
                float(m.iloc[-1].under5_mortality_per_1000 - m.iloc[0].under5_mortality_per_1000), 2
            ),
        )
    model_result = {"status": "Skipped: insufficient paired observations"}
    if len(paired) >= 5:
        X = paired[["basic_sanitation_pct"]]
        y = paired["under5_mortality_per_1000"]
        model = LinearRegression().fit(X, y)
        pred = model.predict(X)
        model_result = {
            "status": "In-sample descriptive regression",
            "predictor": "Basic sanitation access (%)",
            "target": "Under-five mortality per 1,000 live births",
            "n": int(len(paired)),
            "intercept": round(float(model.intercept_), 4),
            "slope_per_percentage_point": round(float(model.coef_[0]), 4),
            "r_squared_in_sample": round(float(r2_score(y, pred)), 3),
            "mae_in_sample": round(float(mean_absolute_error(y, pred)), 3),
            "caution": "Observational time-series association; not a causal effect or validated forecast.",
        }
        stats["pearson_correlation"] = round(
            float(paired.basic_sanitation_pct.corr(paired.under5_mortality_per_1000)), 3
        )
    return stats, model_result


def charts(df):
    plt.figure(figsize=(9, 5))
    plt.plot(df.year, df.basic_sanitation_pct, marker="o", linewidth=2)
    plt.xlabel("Year")
    plt.ylabel("Population with at least basic sanitation (%)")
    plt.title("India: basic sanitation access over time")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUT / "sanitation_trend.png", dpi=180)
    plt.close()

    p = df.dropna(subset=list(INDICATORS.values()))
    plt.figure(figsize=(7, 5))
    plt.scatter(p.basic_sanitation_pct, p.under5_mortality_per_1000, alpha=0.8)
    plt.xlabel("Basic sanitation access (%)")
    plt.ylabel("Under-five mortality (per 1,000 live births)")
    plt.title("Sanitation and child mortality: descriptive association")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUT / "sanitation_mortality_scatter.png", dpi=180)
    plt.close()


def report(stats, model):
    lines = [
        "# India Sanitation & Child Survival: Policy Analytics",
        "",
        "## Research question",
        "How did basic sanitation access and under-five mortality change in India, and how closely did they move together?",
        "",
        "## Data and workflow",
        "- Source: World Bank World Development Indicators public API.",
        "- Geography/period: India, requested 2000–2022; API coverage may vary.",
        "- Indicators: basic sanitation (% population; SH.STA.BASS.ZS) and under-five mortality (per 1,000 live births; SH.DYN.MORT).",
        "- Steps: API retrieval, merge by year, type conversion, missingness review, EDA, descriptive statistics, charts, linear regression.",
        "",
        "## Findings",
    ]
    if "sanitation_change_percentage_points" in stats:
        lines.append(
            f"- Sanitation: {stats['sanitation_start_pct']}% in {stats['sanitation_start_year']} to {stats['sanitation_end_pct']}% in {stats['sanitation_end_year']} ({stats['sanitation_change_percentage_points']} percentage points)."
        )
    if "mortality_change" in stats:
        lines.append(
            f"- Under-five mortality: {stats['mortality_start_rate']} in {stats['mortality_start_year']} to {stats['mortality_end_rate']} in {stats['mortality_end_year']} per 1,000 live births."
        )
    if "pearson_correlation" in stats:
        lines.append(
            f"- Pearson correlation across {stats['paired_years']} paired years: {stats['pearson_correlation']}."
        )
    lines += ["", "## Model", f"- {model['status']}"]
    if "slope_per_percentage_point" in model:
        lines.append(
            f"- Slope: {model['slope_per_percentage_point']}; in-sample R²: {model['r_squared_in_sample']}; MAE: {model['mae_in_sample']}."
        )
    lines += [
        "",
        "## Interpretation and limitations",
        "- Correlation does not show that sanitation caused mortality changes.",
        "- Income, nutrition, immunization, healthcare access, education, water quality, and measurement changes may affect both indicators.",
        "- National annual averages hide state, district, rural/urban, and household inequalities.",
        "- The regression is an introductory demonstration, not a causal evaluation or validated forecast.",
        "",
        "## Policy-relevant next steps",
        "1. Extend to state-level data where comparable observations exist.",
        "2. Add contextual indicators such as drinking-water access, poverty, immunization, and health-service coverage.",
        "3. Use a defensible evaluation design and comparison group for impact assessment.",
        "",
        "## Reproducibility",
        "Run `python analysis.py`; outputs are saved in `outputs/`.",
        "## Source links",
        "- https://data.worldbank.org/indicator/SH.STA.BASS.ZS?locations=IN",
        "- https://data.worldbank.org/indicator/SH.DYN.MORT?locations=IN",
        "- https://datahelpdesk.worldbank.org/knowledgebase/articles/889386-developer-information-overview",
    ]
    (OUT / "policy_brief.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    print("Fetching public World Bank data...")
    df = get_data()
    if df.empty:
        raise RuntimeError("No usable data returned.")
    df.to_csv(OUT / "india_sanitation_mortality_clean.csv", index=False)
    stats, model = analyze(df)
    charts(df)
    report(stats, model)
    (OUT / "summary_statistics.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    (OUT / "model_results.json").write_text(json.dumps(model, indent=2), encoding="utf-8")
    print("Completed. Review the outputs/ folder.")
    print(json.dumps(stats, indent=2))
    print(json.dumps(model, indent=2))


if __name__ == "__main__":
    main()
