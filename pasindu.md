Features + Model

Step 1: Take this file from Member 1:
data/gold/final_dataset.csv

Step 2: Create feature engineering code here:
src/features/build_features.py

Create:
monthly_avg_sales, historical_max_sales, sales_std, growth_rate, order_frequency, inactive_days, seasonality_score, poi_score

Step 3: Save model-ready dataset here:
data/gold/model_features.csv

Step 4: Create latent demand logic here:
src/models/censored_regression.py

Step 5: Train/refine model here:
src/models/train_model.py

Step 6: Generate final predictions here:
src/models/predict.py

Step 7: Save final CSV here:
outputs/predictions/teamname_predictions.csv

Required columns:
Outlet_ID, Maximum_Monthly_Liters