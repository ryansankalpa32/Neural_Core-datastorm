Pipeline + Cleaning

Step 1: Put raw CSV files here:
data/bronze/

Step 2: Create/load data script:
src/data_pipeline/ingest.py

Step 3: Create reusable cleaning checks here:
src/data_pipeline/clean.py

Add checks for:
nulls, duplicates, invalid ranges, invalid dates, invalid coordinates

Step 4: Save bad records here:
data/rejected/

Example files:
data/rejected/rejected_transactions.csv
data/rejected/rejected_outlets.csv

Step 5: Save cleaned files here:
data/silver/

Example:
data/silver/transactions_clean.csv
data/silver/outlets_clean.csv
data/silver/seasonality_clean.csv
data/silver/holidays_clean.csv

Step 6: Merge cleaned datasets here:
src/data_pipeline/transform.py

Step 7: Save final merged clean dataset here:
data/gold/final_dataset.csv