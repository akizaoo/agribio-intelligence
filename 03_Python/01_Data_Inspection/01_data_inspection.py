import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# AGRIBIO INTELLIGENCE PROJECT
# DATA CLEANING AND EXPLORATORY DATA ANALYSIS
# ============================================================

print("=" * 70)
print("AGRIBIO INTELLIGENCE - DATA CLEANING AND ANALYSIS")
print("=" * 70)

# ============================================================
# STEP 1: FIND CSV DATASET AUTOMATICALLY
# ============================================================

current_folder = Path.cwd()

csv_files = list(current_folder.rglob("*.csv"))

# Remove output files if they already exist
csv_files = [
    file for file in csv_files
    if "cleaned" not in file.name.lower()
]

if len(csv_files) == 0:
    print("\nNo CSV file found automatically.")
    print("Please enter the full path of your CSV file.")

    file_path = input("Enter CSV file path: ").strip()

    df = pd.read_csv(file_path)

else:
    print("\nCSV files found:")

    for i, file in enumerate(csv_files):
        print(f"{i + 1}. {file}")

    # Automatically select first CSV file
    file_path = csv_files[0]

    print(f"\nUsing dataset: {file_path}")

    df = pd.read_csv(file_path)


# ============================================================
# STEP 2: INITIAL DATA INSPECTION
# ============================================================

print("\n" + "=" * 70)
print("DATASET PREVIEW")
print("=" * 70)

print(df.head())

print("\n" + "=" * 70)
print("DATASET SHAPE")
print("=" * 70)

print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")


print("\n" + "=" * 70)
print("COLUMN INFORMATION")
print("=" * 70)

print(df.info())


print("\n" + "=" * 70)
print("DATA TYPES")
print("=" * 70)

print(df.dtypes)


# ============================================================
# STEP 3: CHECK MISSING VALUES
# ============================================================

print("\n" + "=" * 70)
print("MISSING VALUES BEFORE CLEANING")
print("=" * 70)

missing_before = df.isnull().sum()

print(missing_before)


# ============================================================
# STEP 4: REMOVE DUPLICATES
# ============================================================

print("\n" + "=" * 70)
print("DUPLICATE RECORDS")
print("=" * 70)

duplicates = df.duplicated().sum()

print(f"Duplicate rows before cleaning: {duplicates}")

df = df.drop_duplicates()

print(f"Duplicate rows after cleaning: {df.duplicated().sum()}")


# ============================================================
# STEP 5: HANDLE MISSING NUMERICAL VALUES
# ============================================================

print("\n" + "=" * 70)
print("HANDLING NUMERICAL MISSING VALUES")
print("=" * 70)

numerical_columns = df.select_dtypes(include=["int64", "float64"]).columns

for column in numerical_columns:

    if df[column].isnull().sum() > 0:

        median_value = df[column].median()

        df[column] = df[column].fillna(median_value)

        print(
            f"Filled missing values in '{column}' "
            f"using median: {median_value}"
        )


# ============================================================
# STEP 6: HANDLE MISSING CATEGORICAL VALUES
# ============================================================

print("\n" + "=" * 70)
print("HANDLING CATEGORICAL MISSING VALUES")
print("=" * 70)

categorical_columns = df.select_dtypes(include=["object"]).columns

for column in categorical_columns:

    if df[column].isnull().sum() > 0:

        mode_value = df[column].mode()[0]

        df[column] = df[column].fillna(mode_value)

        print(
            f"Filled missing values in '{column}' "
            f"using mode: {mode_value}"
        )


# ============================================================
# STEP 7: CHECK MISSING VALUES AFTER CLEANING
# ============================================================

print("\n" + "=" * 70)
print("MISSING VALUES AFTER CLEANING")
print("=" * 70)

missing_after = df.isnull().sum()

print(missing_after)


# ============================================================
# STEP 8: STATISTICAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("STATISTICAL SUMMARY")
print("=" * 70)

print(df.describe())


# ============================================================
# STEP 9: CORRELATION MATRIX
# ============================================================

print("\n" + "=" * 70)
print("CORRELATION MATRIX")
print("=" * 70)

numerical_data = df.select_dtypes(include=["int64", "float64"])

correlation_matrix = numerical_data.corr()

print(correlation_matrix)


# ============================================================
# STEP 10: SAVE CLEANED DATASET
# ============================================================

output_folder = Path("project_outputs")

output_folder.mkdir(exist_ok=True)

cleaned_file = output_folder / "cleaned_agricultural_data.csv"

df.to_csv(cleaned_file, index=False)

print("\n" + "=" * 70)
print("CLEANED DATASET SAVED")
print("=" * 70)

print(f"Saved at: {cleaned_file}")


# ============================================================
# STEP 11: SAVE STATISTICAL SUMMARY
# ============================================================

summary_file = output_folder / "statistical_summary.csv"

df.describe().to_csv(summary_file)

print(f"Statistical summary saved at: {summary_file}")


# ============================================================
# STEP 12: CREATE CORRELATION HEATMAP
# ============================================================

plt.figure(figsize=(10, 8))

plt.imshow(correlation_matrix, aspect="auto")

plt.colorbar()

plt.xticks(
    range(len(correlation_matrix.columns)),
    correlation_matrix.columns,
    rotation=45,
    ha="right"
)

plt.yticks(
    range(len(correlation_matrix.columns)),
    correlation_matrix.columns
)

plt.title("Correlation Matrix - Agricultural Dataset")

plt.tight_layout()

plt.savefig(
    output_folder / "correlation_matrix.png",
    dpi=300
)

plt.close()


# ============================================================
# STEP 13: YIELD DISTRIBUTION
# ============================================================

if "Yield" in df.columns:

    plt.figure(figsize=(10, 6))

    plt.hist(
        df["Yield"].dropna(),
        bins=30,
        edgecolor="black"
    )

    plt.xlabel("Yield")

    plt.ylabel("Frequency")

    plt.title("Distribution of Agricultural Yield")

    plt.tight_layout()

    plt.savefig(
        output_folder / "yield_distribution.png",
        dpi=300
    )

    plt.close()


# ============================================================
# STEP 14: PRODUCTION DISTRIBUTION
# ============================================================

if "Production" in df.columns:

    plt.figure(figsize=(10, 6))

    plt.hist(
        df["Production"].dropna(),
        bins=30,
        edgecolor="black"
    )

    plt.xlabel("Production")

    plt.ylabel("Frequency")

    plt.title("Distribution of Agricultural Production")

    plt.tight_layout()

    plt.savefig(
        output_folder / "production_distribution.png",
        dpi=300
    )

    plt.close()


# ============================================================
# STEP 15: ANNUAL RAINFALL VS YIELD
# ============================================================

if "Annual_Rainfall" in df.columns and "Yield" in df.columns:

    plt.figure(figsize=(10, 6))

    plt.scatter(
        df["Annual_Rainfall"],
        df["Yield"],
        alpha=0.5
    )

    plt.xlabel("Annual Rainfall")

    plt.ylabel("Yield")

    plt.title("Annual Rainfall vs Agricultural Yield")

    plt.tight_layout()

    plt.savefig(
        output_folder / "rainfall_vs_yield.png",
        dpi=300
    )

    plt.close()


# ============================================================
# STEP 16: FERTILIZER VS YIELD
# ============================================================

if "Fertilizer" in df.columns and "Yield" in df.columns:

    plt.figure(figsize=(10, 6))

    plt.scatter(
        df["Fertilizer"],
        df["Yield"],
        alpha=0.5
    )

    plt.xlabel("Fertilizer Usage")

    plt.ylabel("Yield")

    plt.title("Fertilizer Usage vs Agricultural Yield")

    plt.tight_layout()

    plt.savefig(
        output_folder / "fertilizer_vs_yield.png",
        dpi=300
    )

    plt.close()


# ============================================================
# STEP 17: PESTICIDE VS YIELD
# ============================================================

if "Pesticide" in df.columns and "Yield" in df.columns:

    plt.figure(figsize=(10, 6))

    plt.scatter(
        df["Pesticide"],
        df["Yield"],
        alpha=0.5
    )

    plt.xlabel("Pesticide Usage")

    plt.ylabel("Yield")

    plt.title("Pesticide Usage vs Agricultural Yield")

    plt.tight_layout()

    plt.savefig(
        output_folder / "pesticide_vs_yield.png",
        dpi=300
    )

    plt.close()


# ============================================================
# FINAL PROJECT SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("PROJECT COMPLETED SUCCESSFULLY")
print("=" * 70)

print(f"Original dataset rows: {df.shape[0] + duplicates}")
print(f"Cleaned dataset rows: {df.shape[0]}")
print(f"Total columns: {df.shape[1]}")
print(f"Duplicates removed: {duplicates}")

print("\nProject outputs created:")

for file in output_folder.iterdir():
    print("-", file.name)

print("\nAll analysis files have been saved successfully.")

print("=" * 70)