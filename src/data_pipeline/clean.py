import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_rejected(df: pd.DataFrame, mask: pd.Series, rejected_path: Path, filename: str):
    """Helper function to save rejected/bad rows to the rejected folder."""
    if mask.any():
        rejected_df = df[mask].copy()
        out_file = rejected_path / f"{filename}_rejected.csv"
        rejected_df.to_csv(out_file, index=False)
        logger.warning(f"Saved {len(rejected_df)} bad records to {out_file}")

def clean_outlet_master(bronze_path: Path, silver_path: Path, rejected_path: Path):
    """Clean the outlet_master dataset."""
    logger.info("Cleaning outlet_master...")
    df = pd.read_csv(bronze_path / 'outlet_master.csv')
    
    # Identify bad records (missing Outlet_Size)
    bad_mask = df['Outlet_Size'].isna()
    save_rejected(df, bad_mask, rejected_path, 'outlet_master')
    
    # Impute missing values to keep rows in Silver
    df['Outlet_Size'] = df['Outlet_Size'].fillna('Unknown')
    
    # Standardize string categories
    if 'Outlet_Type' in df.columns:
        df['Outlet_Type'] = df['Outlet_Type'].str.strip().str.title()
        df['Outlet_Type'] = df['Outlet_Type'].replace({'Grocry': 'Grocery'})
    
    df['Outlet_Size'] = df['Outlet_Size'].str.strip().str.title()
    
    output_file = silver_path / 'outlet_master.parquet'
    df.to_parquet(output_file, index=False)
    logger.info(f"Saved cleaned outlet_master to {output_file} (Rows: {len(df)})")

def clean_outlet_coordinates(bronze_path: Path, silver_path: Path, rejected_path: Path):
    """Clean the outlet_coordinates dataset."""
    logger.info("Cleaning outlet_coordinates...")
    df = pd.read_csv(bronze_path / 'outlet_coordinates.csv')
    
    # Convert to numeric to find unparseable ones
    lat_num = pd.to_numeric(df['Latitude'], errors='coerce')
    lon_num = pd.to_numeric(df['Longitude'], errors='coerce')
    
    # Identify bad records: unparseable or outside Sri Lanka bounds (Lat 5.5 to 10.0, Lon 79.0 to 82.0)
    bad_mask = (
        lat_num.isna() | lon_num.isna() |
        (lat_num < 5.5) | (lat_num > 10.0) |
        (lon_num < 79.0) | (lon_num > 82.0)
    )
    save_rejected(df, bad_mask, rejected_path, 'outlet_coordinates')
    
    # Keep them in Silver with NaN coordinates
    df['Latitude'] = lat_num
    df['Longitude'] = lon_num
    
    output_file = silver_path / 'outlet_coordinates.parquet'
    df.to_parquet(output_file, index=False)
    logger.info(f"Saved cleaned outlet_coordinates to {output_file} (Rows: {len(df)})")

def clean_holiday_list(bronze_path: Path, silver_path: Path, rejected_path: Path):
    """Clean the holiday_list dataset."""
    logger.info("Cleaning holiday_list...")
    df = pd.read_csv(bronze_path / 'holiday_list.csv')
    
    # Parse dates
    parsed_dates = pd.to_datetime(df['Date'], errors='coerce')
    
    # Identify bad records (unparseable dates)
    bad_mask = parsed_dates.isna()
    save_rejected(df, bad_mask, rejected_path, 'holiday_list')
    
    df['Date'] = parsed_dates
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    
    output_file = silver_path / 'holiday_list.parquet'
    df.to_parquet(output_file, index=False)
    logger.info(f"Saved cleaned holiday_list to {output_file} (Rows: {len(df)})")

def clean_distributor_seasonality(bronze_path: Path, silver_path: Path, rejected_path: Path):
    """Clean the distributor_seasonality_details dataset."""
    logger.info("Cleaning distributor_seasonality_details...")
    df = pd.read_csv(bronze_path / 'distributor_seasonality_details.csv')
    
    bad_mask = df.isna().any(axis=1)
    save_rejected(df, bad_mask, rejected_path, 'distributor_seasonality')
    
    if 'Seasonality_Index' in df.columns:
        df['Seasonality_Index'] = df['Seasonality_Index'].str.strip().str.title()
    
    output_file = silver_path / 'distributor_seasonality_details.parquet'
    df.to_parquet(output_file, index=False)
    logger.info(f"Saved cleaned distributor_seasonality_details to {output_file} (Rows: {len(df)})")

def clean_transactions(bronze_path: Path, silver_path: Path, rejected_path: Path):
    """Clean the transactions_history_final dataset."""
    logger.info("Cleaning transactions_history_final (This may take a minute)...")
    df = pd.read_csv(bronze_path / 'transactions_history_final.csv')
    
    # Identify bad records: negatives or exact duplicates
    bad_mask = pd.Series(False, index=df.index)
    if 'Volume_Liters' in df.columns:
        bad_mask = bad_mask | (df['Volume_Liters'] < 0)
    if 'Total_Bill_Value' in df.columns:
        bad_mask = bad_mask | (df['Total_Bill_Value'] < 0)
        
    is_duplicate = df.duplicated(keep='first')
    bad_mask = bad_mask | is_duplicate
    
    save_rejected(df, bad_mask, rejected_path, 'transactions_history')
    
    # Fix and keep in Silver
    if 'Volume_Liters' in df.columns:
        df['Volume_Liters'] = df['Volume_Liters'].clip(lower=0)
    if 'Total_Bill_Value' in df.columns:
        df['Total_Bill_Value'] = df['Total_Bill_Value'].clip(lower=0)
        
    df = df[~is_duplicate] # actually drop duplicates from silver since they add zero value
    
    output_file = silver_path / 'transactions_history.parquet'
    df.to_parquet(output_file, index=False)
    logger.info(f"Saved cleaned transactions to {output_file} (Rows: {len(df)})")

def main():
    bronze_path = Path("data/bronze")
    silver_path = Path("data/silver")
    rejected_path = Path("data/rejected")
    
    # Ensure directories exist
    silver_path.mkdir(parents=True, exist_ok=True)
    rejected_path.mkdir(parents=True, exist_ok=True)
    
    try:
        clean_outlet_master(bronze_path, silver_path, rejected_path)
        clean_outlet_coordinates(bronze_path, silver_path, rejected_path)
        clean_holiday_list(bronze_path, silver_path, rejected_path)
        clean_distributor_seasonality(bronze_path, silver_path, rejected_path)
        clean_transactions(bronze_path, silver_path, rejected_path)
        logger.info("All Bronze to Silver data cleaning completed successfully.")
    except Exception as e:
        logger.error(f"Data cleaning failed: {e}")

if __name__ == "__main__":
    main()
