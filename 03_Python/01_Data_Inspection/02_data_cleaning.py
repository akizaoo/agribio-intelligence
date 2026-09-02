# ============================================================
# AGRIBIO INTELLIGENCE
# COMPLETE AGRICULTURAL DATA ANALYSIS PROJECT
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT = Path(r"C:\Users\PC\Desktop\Agribio-Intelligence")

RAW_FOLDER = PROJECT / "02_Data" / "Raw"
OUTPUT_FOLDER = PROJECT / "02_Data" / "Processed"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

print("=" * 75)
print("             AGRIBIO INTELLIGENCE")
print("       AGRICULTURAL DATA ANALYTICS SYSTEM")
print("=" * 75)


# ============================================================
# 2. FIND CSV AUTOMATICALLY
# ============================================================

csv_files = list(RAW_FOLDER.rglob("*.csv"))

if not csv_files:
    print("\nERROR: No CSV file found.")
    print("Expected location:", RAW_FOLDER)
    input("\nPress Enter to exit...")
    raise SystemExit

# Prefer original dataset over previously generated files
original_files = [
    f for f in csv_files
    if "cleaned" not in f.name.lower()
    and "summary" not in f.name.lower()
    and "correlation" not in f.name.lower()
]

if original_files:
    file_path = original_files[0]
else:
    file_path = csv_files[0]

print("\nDataset selected:")
print(file_path)


# ============================================================
# 3. LOAD DATA
# ============================================================

try:
    df = pd.read_csv(file_path)
except Exception as e:
    print("\nCould not read CSV:")
    print(e)
    input("\nPress Enter to exit...")
    raise SystemExit

original_rows = len(df)
original_columns = len(df.columns)

print("\nDataset loaded successfully!")
print("Rows:", original_rows)
print("Columns:", original_columns)


# ============================================================
# 4. STANDARDIZE COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)

print("\nColumns detected:")
print(df.columns.tolist())


# ============================================================
# 5. BASIC DATA INSPECTION
# ============================================================

inspection = pd.DataFrame({
    "Column": df.columns,
    "Data_Type": [str(df[c].dtype) for c in df.columns],
    "Missing_Values": [df[c].isna().sum() for c in df.columns],
    "Unique_Values": [df[c].nunique() for c in df.columns]
})

inspection.to_csv(
    OUTPUT_FOLDER / "data_inspection_report.csv",
    index=False
)

print("\nMissing values BEFORE cleaning:")
print(df.isna().sum())

duplicates_before = df.duplicated().sum()

print("\nDuplicate rows:", duplicates_before)


# ============================================================
# 6. CLEAN DATA
# ============================================================

# Remove duplicate rows
df = df.drop_duplicates()

# Clean text columns
text_columns = df.select_dtypes(include="object").columns

for col in text_columns:
    df[col] = df[col].astype(str).str.strip()

    # Replace common missing-value strings
    df[col] = df[col].replace(
        ["nan", "NaN", "N/A", "NA", "null", "NULL", ""],
        np.nan
    )

# Fill missing values correctly
for col in df.columns:

    if df[col].isna().sum() > 0:

        if pd.api.types.is_numeric_dtype(df[col]):

            median_value = df[col].median()

            if pd.notna(median_value):
                df[col] = df[col].fillna(median_value)

        else:

            mode_value = df[col].mode()

            if len(mode_value) > 0:
                df[col] = df[col].fillna(mode_value.iloc[0])
            else:
                df[col] = df[col].fillna("Unknown")


duplicates_removed = duplicates_before

print("\nCleaning completed!")
print("Duplicates removed:", duplicates_removed)


# ============================================================
# 7. FINAL DATA QUALITY CHECK
# ============================================================

quality_report = pd.DataFrame({
    "Column": df.columns,
    "Missing_After_Cleaning": [
        df[c].isna().sum() for c in df.columns
    ],
    "Unique_Values": [
        df[c].nunique() for c in df.columns
    ],
    "Data_Type": [
        str(df[c].dtype) for c in df.columns
    ]
})

quality_report.to_csv(
    OUTPUT_FOLDER / "data_quality_report.csv",
    index=False
)

print("\nMissing values AFTER cleaning:")
print(df.isna().sum())


# ============================================================
# 8. STATISTICAL ANALYSIS
# ============================================================

numeric_df = df.select_dtypes(include=np.number)

if not numeric_df.empty:

    statistics = numeric_df.describe().T
    statistics.to_csv(
        OUTPUT_FOLDER / "statistical_summary.csv"
    )

    print("\nSTATISTICAL SUMMARY")
    print("-" * 50)
    print(statistics)


# ============================================================
# 9. CORRELATION ANALYSIS
# ============================================================

if len(numeric_df.columns) >= 2:

    correlation = numeric_df.corr()

    correlation.to_csv(
        OUTPUT_FOLDER / "correlation_matrix.csv"
    )

    print("\nCORRELATION MATRIX")
    print("-" * 50)
    print(correlation.round(3))

else:
    correlation = pd.DataFrame()


# ============================================================
# 10. IDENTIFY IMPORTANT COLUMNS
# ============================================================

def find_column(possible_names):

    for name in possible_names:

        for col in df.columns:

            if col.lower() == name.lower():
                return col

    for name in possible_names:

        for col in df.columns:

            if name.lower() in col.lower():
                return col

    return None


yield_col = find_column([
    "Yield",
    "Crop_Yield",
    "Yield_ton_per_hectare",
    "Yield_tons_per_hectare"
])

production_col = find_column([
    "Production",
    "Crop_Production"
])

rainfall_col = find_column([
    "Annual_Rainfall",
    "Rainfall",
    "Rainfall_mm"
])

fertilizer_col = find_column([
    "Fertilizer",
    "Fertilizer_kg"
])

pesticide_col = find_column([
    "Pesticide",
    "Pesticide_kg"
])

crop_col = find_column([
    "Crop",
    "Crop_Name"
])

season_col = find_column([
    "Season"
])

state_col = find_column([
    "State",
    "Location",
    "Region"
])

print("\nIMPORTANT VARIABLES FOUND")
print("-" * 50)
print("Crop:", crop_col)
print("Yield:", yield_col)
print("Production:", production_col)
print("Rainfall:", rainfall_col)
print("Fertilizer:", fertilizer_col)
print("Pesticide:", pesticide_col)
print("Season:", season_col)
print("Location:", state_col)


# ============================================================
# 11. CROP PERFORMANCE ANALYSIS
# ============================================================

if crop_col and yield_col:

    crop_performance = (
        df.groupby(crop_col)[yield_col]
        .agg(["count", "mean", "median", "min", "max"])
        .sort_values("mean", ascending=False)
    )

    crop_performance.columns = [
        "Records",
        "Average_Yield",
        "Median_Yield",
        "Minimum_Yield",
        "Maximum_Yield"
    ]

    crop_performance["Performance_Score"] = (
        crop_performance["Average_Yield"]
        / crop_performance["Average_Yield"].max()
        * 100
    )

    crop_performance.to_csv(
        OUTPUT_FOLDER / "crop_performance_analysis.csv"
    )

    print("\nTOP CROPS BY AVERAGE YIELD")
    print(crop_performance.head(10))


# ============================================================
# 12. CROP RECOMMENDATION ENGINE
# ============================================================

if crop_col and yield_col:

    recommendation = crop_performance.copy()

    recommendation["Recommendation"] = np.where(
        recommendation["Performance_Score"] >= 75,
        "Highly Recommended",
        np.where(
            recommendation["Performance_Score"] >= 50,
            "Recommended",
            "Needs Further Analysis"
        )
    )

    recommendation = recommendation.sort_values(
        "Performance_Score",
        ascending=False
    )

    recommendation.to_csv(
        OUTPUT_FOLDER / "crop_recommendation.csv"
    )

    print("\nCROP RECOMMENDATION")
    print("-" * 50)
    print(
        recommendation[
            [
                "Average_Yield",
                "Performance_Score",
                "Recommendation"
            ]
        ].head(10)
    )


# ============================================================
# 13. RAINFALL + YIELD ANALYSIS
# ============================================================

if rainfall_col and yield_col:

    rainfall_yield = df[
        [rainfall_col, yield_col]
    ].corr().iloc[0, 1]

    print("\nRainfall-Yield correlation:",
          round(rainfall_yield, 3))

    rainfall_analysis = pd.DataFrame({
        "Metric": ["Rainfall-Yield Correlation"],
        "Value": [rainfall_yield]
    })

    rainfall_analysis.to_csv(
        OUTPUT_FOLDER / "rainfall_yield_analysis.csv",
        index=False
    )


# ============================================================
# 14. INPUT EFFICIENCY ANALYSIS
# ============================================================

if yield_col:

    efficiency = pd.DataFrame(index=df.index)

    efficiency["Yield"] = df[yield_col]

    if fertilizer_col:
        efficiency["Fertilizer"] = df[fertilizer_col]

        efficiency["Yield_per_Fertilizer"] = (
            df[yield_col] /
            df[fertilizer_col].replace(0, np.nan)
        )

    if pesticide_col:
        efficiency["Pesticide"] = df[pesticide_col]

        efficiency["Yield_per_Pesticide"] = (
            df[yield_col] /
            df[pesticide_col].replace(0, np.nan)
        )

    efficiency = efficiency.replace(
        [np.inf, -np.inf],
        np.nan
    )

    efficiency.to_csv(
        OUTPUT_FOLDER / "input_efficiency_analysis.csv",
        index=False
    )


# ============================================================
# 15. AGRICULTURAL RISK SCORE
# ============================================================

risk = pd.DataFrame(index=df.index)

risk["Risk_Score"] = 0.0

risk_factors = 0

# Rainfall abnormality
if rainfall_col:

    rainfall_mean = df[rainfall_col].mean()
    rainfall_std = df[rainfall_col].std()

    if rainfall_std > 0:

        rainfall_deviation = (
            abs(df[rainfall_col] - rainfall_mean)
            / rainfall_std
        )

        risk["Rainfall_Risk"] = np.clip(
            rainfall_deviation * 25,
            0,
            100
        )

        risk["Risk_Score"] += risk["Rainfall_Risk"]
        risk_factors += 1


# High fertilizer input risk
if fertilizer_col:

    fertilizer_mean = df[fertilizer_col].mean()

    if fertilizer_mean > 0:

        fertilizer_risk = (
            df[fertilizer_col]
            / fertilizer_mean
            * 50
        )

        risk["Input_Risk"] = np.clip(
            fertilizer_risk,
            0,
            100
        )

        risk["Risk_Score"] += risk["Input_Risk"]
        risk_factors += 1


# Pesticide input risk
if pesticide_col:

    pesticide_mean = df[pesticide_col].mean()

    if pesticide_mean > 0:

        pesticide_risk = (
            df[pesticide_col]
            / pesticide_mean
            * 50
        )

        risk["Pesticide_Risk"] = np.clip(
            pesticide_risk,
            0,
            100
        )

        risk["Risk_Score"] += risk["Pesticide_Risk"]
        risk_factors += 1


if risk_factors > 0:

    risk["Risk_Score"] = (
        risk["Risk_Score"] / risk_factors
    )

    risk["Risk_Level"] = pd.cut(
        risk["Risk_Score"],
        bins=[-1, 30, 60, 100],
        labels=["Low", "Medium", "High"]
    )

    risk.to_csv(
        OUTPUT_FOLDER / "agricultural_risk_analysis.csv",
        index=False
    )

    print("\nAGRICULTURAL RISK ANALYSIS CREATED")


# ============================================================
# 16. SUSTAINABILITY SCORE
# ============================================================

sustainability = pd.DataFrame(index=df.index)

sustainability["Sustainability_Score"] = 100.0

penalties = 0

if fertilizer_col:

    fertilizer_level = (
        df[fertilizer_col]
        / df[fertilizer_col].median()
    )

    sustainability["Fertilizer_Pressure"] = np.clip(
        fertilizer_level * 50,
        0,
        100
    )

    sustainability["Sustainability_Score"] -= (
        sustainability["Fertilizer_Pressure"] * 0.25
    )

    penalties += 1


if pesticide_col:

    pesticide_level = (
        df[pesticide_col]
        / df[pesticide_col].median()
    )

    sustainability["Pesticide_Pressure"] = np.clip(
        pesticide_level * 50,
        0,
        100
    )

    sustainability["Sustainability_Score"] -= (
        sustainability["Pesticide_Pressure"] * 0.25
    )

    penalties += 1


sustainability["Sustainability_Score"] = np.clip(
    sustainability["Sustainability_Score"],
    0,
    100
)

sustainability["Sustainability_Level"] = pd.cut(
    sustainability["Sustainability_Score"],
    bins=[-1, 40, 70, 100],
    labels=["Needs Improvement", "Moderate", "Better"]
)

sustainability.to_csv(
    OUTPUT_FOLDER / "sustainability_analysis.csv"
)


# ============================================================
# 17. SIMPLE YIELD PREDICTION MODEL
# ============================================================

if yield_col:

    prediction_features = []

    for col in [
        rainfall_col,
        fertilizer_col,
        pesticide_col,
        production_col
    ]:

        if col and col != yield_col:
            prediction_features.append(col)

    if len(prediction_features) >= 1:

        model_data = df[
            prediction_features + [yield_col]
        ].copy()

        model_data = model_data.replace(
            [np.inf, -np.inf],
            np.nan
        ).dropna()

        X = model_data[prediction_features].astype(float)
        y = model_data[yield_col].astype(float)

        # Standardize variables
        X_mean = X.mean()
        X_std = X.std().replace(0, 1)

        X_scaled = (
            (X - X_mean) / X_std
        )

        # Add intercept
        X_matrix = np.column_stack([
            np.ones(len(X_scaled)),
            X_scaled.values
        ])

        coefficients = np.linalg.lstsq(
            X_matrix,
            y.values,
            rcond=None
        )[0]

        predictions = X_matrix @ coefficients

        # R-squared
        ss_total = np.sum(
            (y.values - y.mean()) ** 2
        )

        ss_residual = np.sum(
            (y.values - predictions) ** 2
        )

        if ss_total != 0:
            r_squared = (
                1 - ss_residual / ss_total
            )
        else:
            r_squared = 0

        prediction_results = model_data.copy()

        prediction_results["Predicted_Yield"] = predictions

        prediction_results["Prediction_Error"] = (
            prediction_results[yield_col]
            - prediction_results["Predicted_Yield"]
        )

        prediction_results.to_csv(
            OUTPUT_FOLDER / "yield_prediction_results.csv",
            index=False
        )

        coefficients_report = pd.DataFrame({
            "Feature": ["Intercept"] + prediction_features,
            "Coefficient": coefficients
        })

        coefficients_report.to_csv(
            OUTPUT_FOLDER / "yield_prediction_model.csv",
            index=False
        )

        print("\nYIELD PREDICTION MODEL")
        print("-" * 50)
        print("Features:", prediction_features)
        print("R-squared:", round(r_squared, 3))

    else:
        print(
            "\nNot enough numerical variables "
            "for yield prediction."
        )


# ============================================================
# 18. SEASONAL ANALYSIS
# ============================================================

if season_col and yield_col:

    seasonal = (
        df.groupby(season_col)[yield_col]
        .agg(["count", "mean", "median"])
        .sort_values("mean", ascending=False)
    )

    seasonal.to_csv(
        OUTPUT_FOLDER / "seasonal_yield_analysis.csv"
    )

    print("\nSEASONAL YIELD ANALYSIS")
    print(seasonal)


# ============================================================
# 19. LOCATION ANALYSIS
# ============================================================

if state_col and yield_col:

    location_analysis = (
        df.groupby(state_col)[yield_col]
        .agg(["count", "mean", "median"])
        .sort_values("mean", ascending=False)
    )

    location_analysis.to_csv(
        OUTPUT_FOLDER / "location_yield_analysis.csv"
    )

    print("\nLOCATION ANALYSIS")
    print(location_analysis.head(10))


# ============================================================
# 20. VISUALIZATION - YIELD
# ============================================================

if yield_col:

    plt.figure(figsize=(9, 5))

    plt.hist(
        df[yield_col],
        bins=30
    )

    plt.title("Crop Yield Distribution")
    plt.xlabel("Yield")
    plt.ylabel("Frequency")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_FOLDER / "01_yield_distribution.png"
    )

    plt.close()


# ============================================================
# 21. VISUALIZATION - PRODUCTION
# ============================================================

if production_col:

    plt.figure(figsize=(9, 5))

    plt.hist(
        df[production_col],
        bins=30
    )

    plt.title("Agricultural Production Distribution")
    plt.xlabel("Production")
    plt.ylabel("Frequency")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_FOLDER / "02_production_distribution.png"
    )

    plt.close()


# ============================================================
# 22. VISUALIZATION - RAINFALL VS YIELD
# ============================================================

if rainfall_col and yield_col:

    plt.figure(figsize=(9, 5))

    plt.scatter(
        df[rainfall_col],
        df[yield_col],
        alpha=0.6
    )

    plt.title("Rainfall vs Crop Yield")
    plt.xlabel("Annual Rainfall")
    plt.ylabel("Crop Yield")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_FOLDER / "03_rainfall_vs_yield.png"
    )

    plt.close()


# ============================================================
# 23. VISUALIZATION - FERTILIZER VS YIELD
# ============================================================

if fertilizer_col and yield_col:

    plt.figure(figsize=(9, 5))

    plt.scatter(
        df[fertilizer_col],
        df[yield_col],
        alpha=0.6
    )

    plt.title("Fertilizer Usage vs Crop Yield")
    plt.xlabel("Fertilizer")
    plt.ylabel("Crop Yield")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_FOLDER / "04_fertilizer_vs_yield.png"
    )

    plt.close()


# ============================================================
# 24. VISUALIZATION - CROP PERFORMANCE
# ============================================================

if crop_col and yield_col:

    top_crops = (
        df.groupby(crop_col)[yield_col]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    plt.figure(figsize=(10, 6))

    top_crops.sort_values().plot(
        kind="barh"
    )

    plt.title("Top 10 Crops by Average Yield")
    plt.xlabel("Average Yield")
    plt.ylabel("Crop")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_FOLDER / "05_top_crop_performance.png"
    )

    plt.close()


# ============================================================
# 25. CORRELATION HEATMAP
# ============================================================

if len(correlation.columns) >= 2:

    plt.figure(figsize=(10, 8))

    plt.imshow(
        correlation,
        cmap="coolwarm",
        aspect="auto"
    )

    plt.colorbar(label="Correlation")

    plt.xticks(
        range(len(correlation.columns)),
        correlation.columns,
        rotation=45,
        ha="right"
    )

    plt.yticks(
        range(len(correlation.columns)),
        correlation.columns
    )

    plt.title(
        "Agricultural Variables Correlation Matrix"
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_FOLDER / "06_correlation_heatmap.png"
    )

    plt.close()


# ============================================================
# 26. SAVE CLEANED DATA
# ============================================================

cleaned_file = (
    OUTPUT_FOLDER /
    "cleaned_crop_yield.csv"
)

df.to_csv(
    cleaned_file,
    index=False
)


# ============================================================
# 27. PROJECT SUMMARY
# ============================================================

summary = {
    "Project": "AgriBio Intelligence",
    "Original_Rows": original_rows,
    "Final_Rows": len(df),
    "Columns": len(df.columns),
    "Duplicates_Removed": duplicates_removed,
    "Yield_Column": yield_col,
    "Production_Column": production_col,
    "Rainfall_Column": rainfall_col,
    "Fertilizer_Column": fertilizer_col,
    "Pesticide_Column": pesticide_col,
    "Crop_Column": crop_col,
    "Season_Column": season_col,
    "Location_Column": state_col
}

summary_df = pd.DataFrame(
    list(summary.items()),
    columns=["Metric", "Value"]
)

summary_df.to_csv(
    OUTPUT_FOLDER / "project_summary.csv",
    index=False
)


# ============================================================
# 28. FINAL OUTPUT
# ============================================================

print("\n")
print("=" * 75)
print("             AGRIBIO INTELLIGENCE COMPLETE")
print("=" * 75)

print("\nFinal dataset:")
print(df.shape)

print("\nDuplicates removed:")
print(duplicates_removed)

print("\nOutput folder:")
print(OUTPUT_FOLDER)

print("\nFiles created:")

for file in sorted(OUTPUT_FOLDER.iterdir()):
    print(" -", file.name)

print("\n" + "=" * 75)
print("ALL AVAILABLE ANALYSIS MODULES COMPLETED")
print("=" * 75)