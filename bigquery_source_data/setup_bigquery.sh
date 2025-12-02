#!/bin/bash

# Script to set up BigQuery dataset and tables from CSV files
# This script creates the dataset, loads CSV files as tables, and creates a view
#
# IMPORTANT: Run this script OUTSIDE of any virtual environment to avoid
# conflicts with gcloud/bq Python dependencies.

set -e  # Exit on error

# Check if we're in a virtual environment and warn
if [ -n "$VIRTUAL_ENV" ]; then
    echo "⚠️  WARNING: Virtual environment detected: $VIRTUAL_ENV"
    echo "⚠️  Please deactivate it first: deactivate"
    echo "⚠️  gcloud/bq commands can conflict with venv Python packages"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Please run: deactivate && ./setup_bigquery.sh"
        exit 1
    fi
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load environment variables from .env file
if [ -f "$PROJECT_ROOT/.env" ]; then
    # Source the .env file to load variables
    set -a  # automatically export all variables
    source "$PROJECT_ROOT/.env"
    set +a  # stop automatically exporting
else
    echo "Error: .env file not found at $PROJECT_ROOT/.env"
    exit 1
fi

# Check required environment variables
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "Error: GOOGLE_CLOUD_PROJECT not set in .env file"
    exit 1
fi

# Use BIGQUERY_DATASET from .env or default to save_the_chickens
DATASET_NAME="${BIGQUERY_DATASET:-save_the_chickens}"
PROJECT_ID="$GOOGLE_CLOUD_PROJECT"
# bq commands use project:dataset format, not project.dataset
DATASET_ID="${PROJECT_ID}:${DATASET_NAME}"

echo "=========================================="
echo "BigQuery Dataset Setup"
echo "=========================================="
echo "Project ID: $PROJECT_ID"
echo "Dataset: $DATASET_NAME"
echo "Full Dataset ID: $DATASET_ID"
echo "=========================================="
echo ""

# Step 1: Create dataset if it doesn't exist
echo "Step 1: Creating dataset (if it doesn't exist)..."
# bq mk uses project:dataset format
bq mk --dataset \
    --location=US \
    --description="Chicken product retail data, waste tracking, and optimization" \
    "$DATASET_ID" 2>/dev/null && echo "✅ Dataset created" || echo "ℹ️  Dataset already exists or error occurred (this is OK if it already exists)"
echo ""

# Step 2: Create tables from CSV files
echo "Step 2: Creating tables from CSV files..."

# Table 1: ProductMasterData
echo "  Creating ProductMasterData table..."
bq load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --autodetect \
    --replace \
    "${DATASET_ID}.ProductMasterData" \
    "$SCRIPT_DIR/ProductMasterData.csv"
echo "  ✅ ProductMasterData table created"

# Table 2: product_sales
echo "  Creating product_sales table..."
bq load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --autodetect \
    --replace \
    "${DATASET_ID}.product_sales" \
    "$SCRIPT_DIR/product_sales.csv"
echo "  ✅ product_sales table created"

# Table 3: CustomerFeedback
echo "  Creating CustomerFeedback table..."
bq load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --autodetect \
    --replace \
    "${DATASET_ID}.CustomerFeedback" \
    "$SCRIPT_DIR/CustomerFeedback.csv"
echo "  ✅ CustomerFeedback table created"

# Table 4: Recipes
echo "  Creating Recipes table..."
bq load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --autodetect \
    --replace \
    "${DATASET_ID}.Recipes" \
    "$SCRIPT_DIR/Recipes.csv"
echo "  ✅ Recipes table created"

# Table 5: WasteTracking
echo "  Creating WasteTracking table..."
bq load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --autodetect \
    --replace \
    "${DATASET_ID}.WasteTracking" \
    "$SCRIPT_DIR/WasteTracking.csv"
echo "  ✅ WasteTracking table created"

# Table 6: Stores
echo "  Creating Stores table..."
bq load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --autodetect \
    --replace \
    "${DATASET_ID}.Stores" \
    "$SCRIPT_DIR/Stores.csv"
echo "  ✅ Stores table created"

# Table 7: DistributionFacilities
echo "  Creating DistributionFacilities table..."
bq load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --autodetect \
    --replace \
    "${DATASET_ID}.DistributionFacilities" \
    "$SCRIPT_DIR/DistributionFacilities.csv"
echo "  ✅ DistributionFacilities table created"

# Table 8: StoreStock
echo "  Creating StoreStock table..."
bq load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --autodetect \
    --replace \
    "${DATASET_ID}.StoreStock" \
    "$SCRIPT_DIR/StoreStock.csv"
echo "  ✅ StoreStock table created"

# Table 9: DistributionStock
echo "  Creating DistributionStock table..."
bq load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --autodetect \
    --replace \
    "${DATASET_ID}.DistributionStock" \
    "$SCRIPT_DIR/DistributionStock.csv"
echo "  ✅ DistributionStock table created"
echo ""

# Step 3: Create view fda_chicken_enforcements
echo "Step 3: Creating fda_chicken_enforcements view..."
# Delete view if it exists, then create it
bq rm -f "${DATASET_ID}.fda_chicken_enforcements" 2>/dev/null || true
bq mk --use_legacy_sql=false \
    --view "
SELECT
  * -- Selects all columns from the source table
FROM
  \`bigquery-public-data.fda_food.food_enforcement\`
WHERE
  product_description LIKE '%chicken%'
" \
    "${DATASET_ID}.fda_chicken_enforcements"
echo "  ✅ fda_chicken_enforcements view created"
echo ""

# Step 4: Create view actuals_vs_forecast
echo "Step 4: Creating actuals_vs_forecast view with AI forecast..."
# Delete view if it exists, then create it
bq rm -f "${DATASET_ID}.actuals_vs_forecast" 2>/dev/null || true

# Create the view with forecast query and union
bq mk --use_legacy_sql=false \
    --view "
WITH
  sales_data AS (
    SELECT 
      EXTRACT(DATE FROM SaleDate) AS date, 
      StoreID,
      ProductNumber, 
      SUM(SalesQuantity) AS sales_quantity
    FROM 
      \`${PROJECT_ID}.${DATASET_NAME}.product_sales\`
    GROUP BY date, StoreID, ProductNumber
  ),
  forecast_data AS (
    SELECT *
    FROM
      AI.FORECAST(
        TABLE sales_data,
        data_col => 'sales_quantity',
        timestamp_col => 'date',
        id_cols => ['StoreID', 'ProductNumber'],
        horizon => 30
      )
  )
SELECT
  t1.SaleDate AS event_timestamp,
  t1.StoreID,
  t1.ProductNumber,
  SUM(t1.SalesQuantity) AS quantity_value,
  NULL AS confidence_level,
  NULL AS prediction_interval_lower_bound,
  NULL AS prediction_interval_upper_bound,
  NULL AS ai_forecast_status,
  'Actual' AS data_type
FROM
  \`${PROJECT_ID}.${DATASET_NAME}.product_sales\` AS t1
GROUP BY t1.SaleDate, t1.StoreID, t1.ProductNumber
UNION ALL
SELECT
  t2.forecast_timestamp AS event_timestamp,
  t2.StoreID,
  t2.ProductNumber,
  CAST(t2.forecast_value AS INT64) AS quantity_value,
  t2.confidence_level,
  t2.prediction_interval_lower_bound,
  t2.prediction_interval_upper_bound,
  t2.ai_forecast_status,
  'Forecast' AS data_type
FROM
  forecast_data AS t2
" \
    "${DATASET_ID}.actuals_vs_forecast"
echo "  ✅ actuals_vs_forecast view created"
echo ""

# Step 5: Create view products_with_recipes
echo "Step 5: Creating products_with_recipes view..."
# Delete view if it exists, then create it
bq rm -f "${DATASET_ID}.products_with_recipes" 2>/dev/null || true
bq mk --use_legacy_sql=false \
    --view "
SELECT
  pm.ProductNumber,
  pm.ProductDescription,
  pm.ProductCategory,
  pm.ShelfLifeDays AS ProductShelfLifeDays,
  pm.StorageRequirements AS ProductStorageRequirements,
  pm.RecipeID,
  r.IngredientName,
  r.IngredientQuantity,
  r.Unit,
  r.PreparationMethod,
  r.IngredientShelfLifeDays
FROM
  \`${PROJECT_ID}.${DATASET_NAME}.ProductMasterData\` AS pm
LEFT JOIN
  \`${PROJECT_ID}.${DATASET_NAME}.Recipes\` AS r
ON
  pm.RecipeID = r.RecipeID
WHERE
  pm.RecipeID IS NOT NULL
ORDER BY
  pm.ProductNumber,
  r.IngredientName
" \
    "${DATASET_ID}.products_with_recipes"
echo "  ✅ products_with_recipes view created"
echo ""

# Step 6: Create view customer_feedback_with_products
echo "Step 6: Creating customer_feedback_with_products view..."
# Delete view if it exists, then create it
bq rm -f "${DATASET_ID}.customer_feedback_with_products" 2>/dev/null || true
bq mk --use_legacy_sql=false \
    --view "
SELECT
  pm.ProductNumber,
  pm.ProductDescription,
  pm.ProductCategory,
  cf.CustomerName,
  cf.ProductName AS FeedbackProductName,
  cf.FeedbackDate,
  cf.Rating,
  cf.Description AS FeedbackDescription
FROM
  \`${PROJECT_ID}.${DATASET_NAME}.CustomerFeedback\` AS cf
LEFT JOIN
  \`${PROJECT_ID}.${DATASET_NAME}.ProductMasterData\` AS pm
ON
  LOWER(pm.ProductDescription) LIKE CONCAT('%', LOWER(cf.ProductName), '%')
ORDER BY
  pm.ProductNumber,
  cf.FeedbackDate DESC
" \
    "${DATASET_ID}.customer_feedback_with_products"
echo "  ✅ customer_feedback_with_products view created"
echo ""

# Step 7: Create view store_stock_current
echo "Step 7: Creating store_stock_current view..."
# Delete view if it exists, then create it
bq rm -f "${DATASET_ID}.store_stock_current" 2>/dev/null || true
bq mk --use_legacy_sql=false \
    --view "
WITH DateOffset AS (
  SELECT DATE_DIFF(CURRENT_DATE(), MAX(StockDate), DAY) AS offset_days
  FROM \`${PROJECT_ID}.${DATASET_NAME}.StoreStock\`
)
SELECT
  s.StoreID,
  s.StoreName,
  s.City,
  s.Postcode,
  s.Latitude,
  s.Longitude,
  ss.StockID,
  ss.ProductNumber,
  pm.ProductDescription,
  pm.ProductCategory,
  pm.ShelfLifeDays,
  DATE_ADD(ss.StockDate, INTERVAL (SELECT offset_days FROM DateOffset) DAY) AS StockDate,
  ss.Quantity,
  DATE_ADD(ss.DeliveryDate, INTERVAL (SELECT offset_days FROM DateOffset) DAY) AS DeliveryDate,
  DATE_ADD(ss.ExpiryDate, INTERVAL (SELECT offset_days FROM DateOffset) DAY) AS ExpiryDate,
  DATE_DIFF(
    DATE_ADD(ss.ExpiryDate, INTERVAL (SELECT offset_days FROM DateOffset) DAY),
    CURRENT_DATE(),
    DAY
  ) AS DaysUntilExpiry,
  ss.BatchNumber,
  ss.StorageLocation
FROM
  \`${PROJECT_ID}.${DATASET_NAME}.StoreStock\` AS ss
JOIN
  \`${PROJECT_ID}.${DATASET_NAME}.Stores\` AS s
ON
  ss.StoreID = s.StoreID
JOIN
  \`${PROJECT_ID}.${DATASET_NAME}.ProductMasterData\` AS pm
ON
  ss.ProductNumber = pm.ProductNumber
WHERE
  ss.StockDate = (
    SELECT MAX(StockDate)
    FROM \`${PROJECT_ID}.${DATASET_NAME}.StoreStock\`
    WHERE StoreID = ss.StoreID AND ProductNumber = ss.ProductNumber
  )
ORDER BY
  s.StoreName,
  pm.ProductDescription,
  DATE_ADD(ss.ExpiryDate, INTERVAL (SELECT offset_days FROM DateOffset) DAY)
" \
    "${DATASET_ID}.store_stock_current"
echo "  ✅ store_stock_current view created"
echo ""

# Step 8: Create view store_stock_expiring_soon
echo "Step 8: Creating store_stock_expiring_soon view..."
# Delete view if it exists, then create it
bq rm -f "${DATASET_ID}.store_stock_expiring_soon" 2>/dev/null || true
bq mk --use_legacy_sql=false \
    --view "
WITH DateOffset AS (
  SELECT DATE_DIFF(CURRENT_DATE(), MAX(StockDate), DAY) AS offset_days
  FROM \`${PROJECT_ID}.${DATASET_NAME}.StoreStock\`
),
StockWithAdjustedDates AS (
  SELECT
    s.StoreID,
    s.StoreName,
    s.City,
    ss.ProductNumber,
    pm.ProductDescription,
    pm.ProductCategory,
    ss.Quantity,
    DATE_ADD(ss.ExpiryDate, INTERVAL (SELECT offset_days FROM DateOffset) DAY) AS ExpiryDate,
    DATE_DIFF(
      DATE_ADD(ss.ExpiryDate, INTERVAL (SELECT offset_days FROM DateOffset) DAY),
      CURRENT_DATE(),
      DAY
    ) AS DaysUntilExpiry,
    ss.BatchNumber,
    ss.StorageLocation
  FROM
    \`${PROJECT_ID}.${DATASET_NAME}.StoreStock\` AS ss
  JOIN
    \`${PROJECT_ID}.${DATASET_NAME}.Stores\` AS s
  ON
    ss.StoreID = s.StoreID
  JOIN
    \`${PROJECT_ID}.${DATASET_NAME}.ProductMasterData\` AS pm
  ON
    ss.ProductNumber = pm.ProductNumber
  WHERE
    ss.StockDate = (
      SELECT MAX(StockDate)
      FROM \`${PROJECT_ID}.${DATASET_NAME}.StoreStock\`
      WHERE StoreID = ss.StoreID AND ProductNumber = ss.ProductNumber
    )
)
SELECT
  StoreID,
  StoreName,
  City,
  ProductNumber,
  ProductDescription,
  ProductCategory,
  Quantity,
  ExpiryDate,
  DaysUntilExpiry,
  BatchNumber,
  StorageLocation,
  CASE
    WHEN DaysUntilExpiry <= 0 THEN 'EXPIRED'
    WHEN DaysUntilExpiry <= 1 THEN 'CRITICAL'
    WHEN DaysUntilExpiry <= 2 THEN 'URGENT'
    ELSE 'WARNING'
  END AS ExpiryStatus
FROM
  StockWithAdjustedDates
WHERE
  ExpiryDate <= DATE_ADD(CURRENT_DATE(), INTERVAL 3 DAY)
ORDER BY
  ExpiryDate,
  StoreName,
  ProductDescription
" \
    "${DATASET_ID}.store_stock_expiring_soon"
echo "  ✅ store_stock_expiring_soon view created"
echo ""

# Step 9: Create view distribution_stock_current
echo "Step 9: Creating distribution_stock_current view..."
# Delete view if it exists, then create it
bq rm -f "${DATASET_ID}.distribution_stock_current" 2>/dev/null || true
bq mk --use_legacy_sql=false \
    --view "
WITH DateOffset AS (
  SELECT DATE_DIFF(CURRENT_DATE(), MAX(StockDate), DAY) AS offset_days
  FROM \`${PROJECT_ID}.${DATASET_NAME}.DistributionStock\`
)
SELECT
  df.FacilityID,
  df.FacilityName,
  df.City,
  df.Postcode,
  df.Latitude,
  df.Longitude,
  ds.StockID,
  ds.ProductNumber,
  pm.ProductDescription,
  pm.ProductCategory,
  pm.ShelfLifeDays,
  DATE_ADD(ds.StockDate, INTERVAL (SELECT offset_days FROM DateOffset) DAY) AS StockDate,
  ds.Quantity,
  DATE_ADD(ds.DeliveryDate, INTERVAL (SELECT offset_days FROM DateOffset) DAY) AS DeliveryDate,
  DATE_ADD(ds.ExpiryDate, INTERVAL (SELECT offset_days FROM DateOffset) DAY) AS ExpiryDate,
  DATE_DIFF(
    DATE_ADD(ds.ExpiryDate, INTERVAL (SELECT offset_days FROM DateOffset) DAY),
    CURRENT_DATE(),
    DAY
  ) AS DaysUntilExpiry,
  ds.BatchNumber,
  ds.StorageLocation
FROM
  \`${PROJECT_ID}.${DATASET_NAME}.DistributionStock\` AS ds
JOIN
  \`${PROJECT_ID}.${DATASET_NAME}.DistributionFacilities\` AS df
ON
  ds.FacilityID = df.FacilityID
JOIN
  \`${PROJECT_ID}.${DATASET_NAME}.ProductMasterData\` AS pm
ON
  ds.ProductNumber = pm.ProductNumber
WHERE
  ds.StockDate = (
    SELECT MAX(StockDate)
    FROM \`${PROJECT_ID}.${DATASET_NAME}.DistributionStock\`
    WHERE FacilityID = ds.FacilityID AND ProductNumber = ds.ProductNumber
  )
ORDER BY
  df.FacilityName,
  pm.ProductDescription,
  DATE_ADD(ds.ExpiryDate, INTERVAL (SELECT offset_days FROM DateOffset) DAY)
" \
    "${DATASET_ID}.distribution_stock_current"
echo "  ✅ distribution_stock_current view created"
echo ""

# Step 10: Create view store_stock_summary
echo "Step 10: Creating store_stock_summary view..."
# Delete view if it exists, then create it
bq rm -f "${DATASET_ID}.store_stock_summary" 2>/dev/null || true
bq mk --use_legacy_sql=false \
    --view "
WITH DateOffset AS (
  SELECT DATE_DIFF(CURRENT_DATE(), MAX(StockDate), DAY) AS offset_days
  FROM \`${PROJECT_ID}.${DATASET_NAME}.StoreStock\`
)
SELECT
  s.StoreID,
  s.StoreName,
  s.City,
  s.Latitude,
  s.Longitude,
  ss.ProductNumber,
  pm.ProductDescription,
  pm.ProductCategory,
  SUM(ss.Quantity) AS TotalQuantity,
  MIN(DATE_ADD(ss.ExpiryDate, INTERVAL (SELECT offset_days FROM DateOffset) DAY)) AS EarliestExpiryDate,
  MAX(DATE_ADD(ss.ExpiryDate, INTERVAL (SELECT offset_days FROM DateOffset) DAY)) AS LatestExpiryDate,
  COUNT(DISTINCT ss.BatchNumber) AS BatchCount,
  AVG(ss.Quantity) AS AvgQuantityPerBatch
FROM
  \`${PROJECT_ID}.${DATASET_NAME}.StoreStock\` AS ss
JOIN
  \`${PROJECT_ID}.${DATASET_NAME}.Stores\` AS s
ON
  ss.StoreID = s.StoreID
JOIN
  \`${PROJECT_ID}.${DATASET_NAME}.ProductMasterData\` AS pm
ON
  ss.ProductNumber = pm.ProductNumber
WHERE
  ss.StockDate = (
    SELECT MAX(StockDate)
    FROM \`${PROJECT_ID}.${DATASET_NAME}.StoreStock\`
    WHERE StoreID = ss.StoreID AND ProductNumber = ss.ProductNumber
  )
GROUP BY
  s.StoreID,
  s.StoreName,
  s.City,
  s.Latitude,
  s.Longitude,
  ss.ProductNumber,
  pm.ProductDescription,
  pm.ProductCategory
ORDER BY
  s.StoreName,
  pm.ProductDescription
" \
    "${DATASET_ID}.store_stock_summary"
echo "  ✅ store_stock_summary view created"
echo ""

# Step 11: Create view store_proximity
echo "Step 11: Creating store_proximity view..."
# Delete view if it exists, then create it
bq rm -f "${DATASET_ID}.store_proximity" 2>/dev/null || true
bq mk --use_legacy_sql=false \
    --view "
SELECT
  s1.StoreID AS StoreFromID,
  s1.StoreName AS StoreFromName,
  s1.City AS StoreFromCity,
  s1.Latitude AS StoreFromLatitude,
  s1.Longitude AS StoreFromLongitude,
  s2.StoreID AS StoreToID,
  s2.StoreName AS StoreToName,
  s2.City AS StoreToCity,
  s2.Latitude AS StoreToLatitude,
  s2.Longitude AS StoreToLongitude,
  ST_DISTANCE(
    ST_GEOGPOINT(s1.Longitude, s1.Latitude),
    ST_GEOGPOINT(s2.Longitude, s2.Latitude)
  ) / 1000 AS DistanceKm,
  CASE
    WHEN s1.City = s2.City THEN 'Same City'
    ELSE 'Different City'
  END AS ProximityType
FROM
  \`${PROJECT_ID}.${DATASET_NAME}.Stores\` AS s1
CROSS JOIN
  \`${PROJECT_ID}.${DATASET_NAME}.Stores\` AS s2
WHERE
  s1.StoreID != s2.StoreID
ORDER BY
  DistanceKm
" \
    "${DATASET_ID}.store_proximity"
echo "  ✅ store_proximity view created"
echo ""

echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo "Dataset: $DATASET_ID"
echo "Tables created:"
echo "  - ProductMasterData"
echo "  - product_sales"
echo "  - CustomerFeedback"
echo "  - Recipes"
echo "  - WasteTracking"
echo "  - Stores"
echo "  - DistributionFacilities"
echo "  - StoreStock"
echo "  - DistributionStock"
echo "Views created:"
echo "  - fda_chicken_enforcements"
echo "  - actuals_vs_forecast (with AI forecast)"
echo "  - products_with_recipes"
echo "  - customer_feedback_with_products"
echo "  - store_stock_current"
echo "  - store_stock_expiring_soon"
echo "  - distribution_stock_current"
echo "  - store_stock_summary"
echo "  - store_proximity"
echo "=========================================="

