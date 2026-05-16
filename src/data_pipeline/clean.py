"""
Bronze → Silver data cleaning pipeline.

Reads raw CSV files from the Bronze lakehouse layer, validates and cleans
each dataset, saves rejected records for auditing, and writes cleaned
Parquet files to the Silver layer.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import logging

from src.utils.config import load_config

logger = logging.getLogger(__name__)

__all__ = [
    "clean_outlet_master",
    "clean_outlet_coordinates",
    "clean_holiday_list",
    "clean_distributor_seasonality",
    "clean_transactions",
    "CleaningResult",
]


# ---------------------------------------------------------------------------
# Column name constants — single source of truth
# ---------------------------------------------------------------------------
class Columns:
    """Centralized column names to avoid magic strings throughout the pipeline."""
    OUTLET_SIZE = "Outlet_Size"
    OUTLET_TYPE = "Outlet_Type"
    LATITUDE = "Latitude"
    LONGITUDE = "Longitude"
    VOLUME_LITERS = "Volume_Liters"
    TOTAL_BILL_VALUE = "Total_Bill_Value"
    DATE = "Date"
    YEAR = "Year"
    MONTH = "Month"
    SEASONALITY_INDEX = "Seasonality_Index"


# ---------------------------------------------------------------------------
# Result dataclass — returned by every cleaning function
# ---------------------------------------------------------------------------
@dataclass
class CleaningResult:
    """Summary of a single dataset's cleaning pass."""
    dataset: str
    rows_in: int
    rows_out: int
    rows_rejected: int
    output_path: Path


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def save_rejected(
    df: pd.DataFrame,
    mask: pd.Series,
    rejected_path: Path,
    filename: str,
) -> int:
    """Save rejected/bad rows to the rejected folder and return the count."""
    rejected_count = int(mask.sum())
    if rejected_count > 0:
        rejected_df = df[mask].copy()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = rejected_path / f"{filename}_rejected_{ts}.csv"
        rejected_df.to_csv(out_file, index=False)
        logger.warning(
            "Saved %d bad records to %s", rejected_count, out_file
        )
    return rejected_count


# ---------------------------------------------------------------------------
# Dataset-specific cleaners
# ---------------------------------------------------------------------------
def clean_outlet_master(
    bronze_path: Path, silver_path: Path, rejected_path: Path
) -> CleaningResult:
    """Clean the outlet_master dataset.

    - Rejects rows with missing Outlet_Size (saved for audit).
    - Imputes missing Outlet_Size as 'Unknown' so Silver retains full volume.
    - Standardises string categories and fixes known typos.
    """
    logger.info("Cleaning outlet_master...")
    df = pd.read_csv(bronze_path / "outlet_master.csv")
    rows_in = len(df)

    # Identify bad records (missing Outlet_Size)
    bad_mask = df[Columns.OUTLET_SIZE].isna()
    rows_rejected = save_rejected(df, bad_mask, rejected_path, "outlet_master")

    # Impute missing values — kept in Silver with a sentinel so joins don't break
    df[Columns.OUTLET_SIZE] = df[Columns.OUTLET_SIZE].fillna("Unknown")

    # Standardize string categories
    if Columns.OUTLET_TYPE in df.columns:
        df[Columns.OUTLET_TYPE] = (
            df[Columns.OUTLET_TYPE].str.strip().str.title()
        )
        df[Columns.OUTLET_TYPE] = df[Columns.OUTLET_TYPE].replace(
            {"Grocry": "Grocery"}
        )

    df[Columns.OUTLET_SIZE] = df[Columns.OUTLET_SIZE].str.strip().str.title()

    output_file = silver_path / "outlet_master.parquet"
    df.to_parquet(output_file, index=False)
    logger.info("Saved cleaned outlet_master to %s (Rows: %d)", output_file, len(df))

    return CleaningResult(
        dataset="outlet_master",
        rows_in=rows_in,
        rows_out=len(df),
        rows_rejected=rows_rejected,
        output_path=output_file,
    )


def clean_outlet_coordinates(
    bronze_path: Path, silver_path: Path, rejected_path: Path
) -> CleaningResult:
    """Clean the outlet_coordinates dataset.

    - Coerces lat/lon to numeric.
    - Flags unparseable and out-of-Sri-Lanka-bounds rows as rejected.
    - Nulls out bad coordinate values in Silver so downstream models
      can decide how to handle missingness.
    """
    logger.info("Cleaning outlet_coordinates...")
    df = pd.read_csv(bronze_path / "outlet_coordinates.csv")
    rows_in = len(df)

    # Convert to numeric to find unparseable values
    lat_num = pd.to_numeric(df[Columns.LATITUDE], errors="coerce")
    lon_num = pd.to_numeric(df[Columns.LONGITUDE], errors="coerce")

    # Sri Lanka bounds: Lat 5.5–10.0, Lon 79.0–82.0
    SRI_LANKA_LAT_MIN, SRI_LANKA_LAT_MAX = 5.5, 10.0
    SRI_LANKA_LON_MIN, SRI_LANKA_LON_MAX = 79.0, 82.0

    unparseable = lat_num.isna() | lon_num.isna()
    out_of_bounds = (
        (lat_num < SRI_LANKA_LAT_MIN) | (lat_num > SRI_LANKA_LAT_MAX)
        | (lon_num < SRI_LANKA_LON_MIN) | (lon_num > SRI_LANKA_LON_MAX)
    )
    bad_mask = unparseable | out_of_bounds
    rows_rejected = save_rejected(df, bad_mask, rejected_path, "outlet_coordinates")

    # Null out bad values so Silver is genuinely clean
    df[Columns.LATITUDE] = lat_num.where(~bad_mask)
    df[Columns.LONGITUDE] = lon_num.where(~bad_mask)

    output_file = silver_path / "outlet_coordinates.parquet"
    df.to_parquet(output_file, index=False)
    logger.info(
        "Saved cleaned outlet_coordinates to %s (Rows: %d)", output_file, len(df)
    )

    return CleaningResult(
        dataset="outlet_coordinates",
        rows_in=rows_in,
        rows_out=len(df),
        rows_rejected=rows_rejected,
        output_path=output_file,
    )


def clean_holiday_list(
    bronze_path: Path, silver_path: Path, rejected_path: Path
) -> CleaningResult:
    """Clean the holiday_list dataset.

    - Parses date strings into datetime.
    - Rejects rows with unparseable dates.
    - Derives Year and Month helper columns.
    """
    logger.info("Cleaning holiday_list...")
    df = pd.read_csv(bronze_path / "holiday_list.csv")
    rows_in = len(df)

    # Parse dates
    parsed_dates = pd.to_datetime(df[Columns.DATE], errors="coerce")

    # Identify bad records (unparseable dates)
    bad_mask = parsed_dates.isna()
    rows_rejected = save_rejected(df, bad_mask, rejected_path, "holiday_list")

    df[Columns.DATE] = parsed_dates
    df[Columns.YEAR] = df[Columns.DATE].dt.year
    df[Columns.MONTH] = df[Columns.DATE].dt.month

    output_file = silver_path / "holiday_list.parquet"
    df.to_parquet(output_file, index=False)
    logger.info("Saved cleaned holiday_list to %s (Rows: %d)", output_file, len(df))

    return CleaningResult(
        dataset="holiday_list",
        rows_in=rows_in,
        rows_out=len(df),
        rows_rejected=rows_rejected,
        output_path=output_file,
    )


def clean_distributor_seasonality(
    bronze_path: Path, silver_path: Path, rejected_path: Path
) -> CleaningResult:
    """Clean the distributor_seasonality_details dataset.

    - Rejects rows with any null values.
    - Standardises Seasonality_Index only if it is a string column.
    """
    logger.info("Cleaning distributor_seasonality_details...")
    df = pd.read_csv(bronze_path / "distributor_seasonality_details.csv")
    rows_in = len(df)

    bad_mask = df.isna().any(axis=1)
    rows_rejected = save_rejected(
        df, bad_mask, rejected_path, "distributor_seasonality"
    )

    # Only apply string standardisation if the column is actually string-typed
    if Columns.SEASONALITY_INDEX in df.columns:
        if pd.api.types.is_string_dtype(df[Columns.SEASONALITY_INDEX]):
            df[Columns.SEASONALITY_INDEX] = (
                df[Columns.SEASONALITY_INDEX].str.strip().str.title()
            )

    output_file = silver_path / "distributor_seasonality_details.parquet"
    df.to_parquet(output_file, index=False)
    logger.info(
        "Saved cleaned distributor_seasonality_details to %s (Rows: %d)",
        output_file,
        len(df),
    )

    return CleaningResult(
        dataset="distributor_seasonality_details",
        rows_in=rows_in,
        rows_out=len(df),
        rows_rejected=rows_rejected,
        output_path=output_file,
    )


def clean_transactions(
    bronze_path: Path, silver_path: Path, rejected_path: Path
) -> CleaningResult:
    """Clean the transactions_history_final dataset.

    - Flags negative Volume_Liters / Total_Bill_Value as bad.
    - Flags exact duplicate rows as bad.
    - Clips negatives to zero and drops duplicates in Silver.
    - Uses chunked reading for memory safety on large files.
    """
    logger.info("Cleaning transactions_history_final (this may take a minute)...")

    source_file = bronze_path / "transactions_history_final.csv"

    # Read in chunks for memory safety
    CHUNK_SIZE = 100_000
    chunks: list[pd.DataFrame] = []
    for chunk in pd.read_csv(source_file, chunksize=CHUNK_SIZE):
        chunks.append(chunk)
    df = pd.concat(chunks, ignore_index=True)
    rows_in = len(df)

    logger.info("Loaded %d rows from transactions file.", rows_in)

    # Identify bad records: negatives or exact duplicates
    bad_mask = pd.Series(False, index=df.index)
    if Columns.VOLUME_LITERS in df.columns:
        bad_mask = bad_mask | (df[Columns.VOLUME_LITERS] < 0)
    if Columns.TOTAL_BILL_VALUE in df.columns:
        bad_mask = bad_mask | (df[Columns.TOTAL_BILL_VALUE] < 0)

    is_duplicate = df.duplicated(keep="first")
    bad_mask = bad_mask | is_duplicate

    rows_rejected = save_rejected(
        df, bad_mask, rejected_path, "transactions_history"
    )

    # Fix and keep in Silver
    if Columns.VOLUME_LITERS in df.columns:
        df[Columns.VOLUME_LITERS] = df[Columns.VOLUME_LITERS].clip(lower=0)
    if Columns.TOTAL_BILL_VALUE in df.columns:
        df[Columns.TOTAL_BILL_VALUE] = df[Columns.TOTAL_BILL_VALUE].clip(lower=0)

    # Drop duplicates — they add zero analytical value
    df = df[~is_duplicate]

    output_file = silver_path / "transactions_history.parquet"
    df.to_parquet(output_file, index=False)
    logger.info("Saved cleaned transactions to %s (Rows: %d)", output_file, len(df))

    return CleaningResult(
        dataset="transactions_history",
        rows_in=rows_in,
        rows_out=len(df),
        rows_rejected=rows_rejected,
        output_path=output_file,
    )


# ---------------------------------------------------------------------------
# Pipeline orchestration
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the full Bronze → Silver cleaning pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Load paths from centralised config
    config = load_config()
    bronze_path = Path(config["data"]["bronze_path"])
    silver_path = Path(config["data"]["silver_path"])
    rejected_path = Path(config["data"].get("rejected_path", "data/rejected"))

    # Ensure output directories exist
    silver_path.mkdir(parents=True, exist_ok=True)
    rejected_path.mkdir(parents=True, exist_ok=True)

    # Ordered cleaning steps
    steps = [
        ("outlet_master", clean_outlet_master),
        ("outlet_coordinates", clean_outlet_coordinates),
        ("holiday_list", clean_holiday_list),
        ("distributor_seasonality", clean_distributor_seasonality),
        ("transactions", clean_transactions),
    ]

    results: list[CleaningResult] = []
    failed: list[str] = []

    for name, func in steps:
        try:
            result = func(bronze_path, silver_path, rejected_path)
            results.append(result)
        except Exception as e:
            logger.error("Failed cleaning %s: %s", name, e, exc_info=True)
            failed.append(name)

    # Print summary report
    if results:
        logger.info("=" * 60)
        logger.info("CLEANING SUMMARY")
        logger.info("=" * 60)
        for r in results:
            logger.info(
                "  %-40s | IN: %6d | OUT: %6d | REJECTED: %4d",
                r.dataset, r.rows_in, r.rows_out, r.rows_rejected,
            )
        logger.info("=" * 60)

    if failed:
        raise RuntimeError(
            f"Bronze → Silver cleaning failed for: {', '.join(failed)}"
        )

    logger.info("All Bronze → Silver data cleaning completed successfully.")


if __name__ == "__main__":
    main()
