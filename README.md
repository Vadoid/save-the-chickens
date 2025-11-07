# Save the Chickens - BigQuery ADK Agent

A conversational AI agent built with Google's Agent Development Kit (ADK) that provides natural language querying and analysis capabilities for chicken product retail operations. This agent is specifically configured to work with the `save_the_chickens` dataset and includes comprehensive evaluation tools for assessing agent performance.

## TLDR

This project creates:
- **BigQuery Dataset**: Chicken product retail data with sales, customer feedback, recipes, and waste tracking (`ProductMasterData`, `product_sales`, `CustomerFeedback`, `Recipes`, `WasteTracking`)
- **Forecast View**: `actuals_vs_forecast` view that combines historical sales with AI-generated 30-day forecasts using [BigQuery's TimesFM model](https://docs.cloud.google.com/bigquery/docs/timesfm-model) via the `AI.FORECAST` function
- **FDA Compliance View**: `fda_chicken_enforcements` view filtering FDA enforcement actions for chicken products
- **AI Agent**: Natural language interface to query and analyze chicken product data, optimize waste reduction, and manage stock using Google's Gemini model

The forecasting uses Google Research's TimesFM foundation model, which is pre-trained on billions of time-points and provides accurate forecasts without requiring model training or management. The system helps optimize chicken delivery, stock management, and decrease waste through intelligent data analysis.

## Overview

The agent uses Google's Gemini model to understand natural language questions about your BigQuery data and automatically generates and executes SQL queries to answer them. It's designed with a focus on chicken product retail operations, waste optimization, stock management, delivery tracking, and regulatory compliance. The system helps retailers minimize waste, optimize inventory, and improve profitability through data-driven insights.

## Narrative: Save the Chickens

**Save the Chickens** is a comprehensive chicken product retail management system designed to optimize operations, reduce waste, and maximize profitability for retailers selling chicken products and byproducts.

### The Challenge

Chicken product retailers face unique challenges:
- **Perishable Inventory**: Chicken products have short shelf lives (2-7 days), requiring precise inventory management
- **Waste Management**: Expired products, damaged goods, and overstock lead to significant financial losses
- **Complex Product Portfolio**: Retailers manage diverse products including whole chickens, parts (breasts, thighs, wings), byproducts (liver, stock, fat), and prepared items (pot pies, empanadas, croissants)
- **Delivery Optimization**: Balancing stock levels with delivery schedules to minimize waste while meeting customer demand
- **Recipe Costing**: Tracking ingredient usage across multiple prepared products to optimize procurement and pricing
- **Regulatory Compliance**: Monitoring FDA enforcement actions and recalls that could impact sales and safety

### The Solution

Save the Chickens provides an AI-powered analytics platform that:

1. **Tracks Complete Product Lifecycle**: From delivery to sale to waste, monitoring every product through its journey
2. **Predicts Demand**: Uses TimesFM AI forecasting to predict 30-day sales patterns, helping optimize inventory levels
3. **Identifies Waste Patterns**: Analyzes waste by product, reason (expired, damaged, overstock), and cost to identify optimization opportunities
4. **Monitors Expiration Risk**: Tracks products approaching their due dates and recommends discount strategies or delivery adjustments
5. **Optimizes Recipes**: Tracks ingredient usage across products to optimize procurement and reduce costs
6. **Ensures Compliance**: Monitors FDA enforcement actions for chicken products to ensure regulatory compliance
7. **Analyzes Customer Feedback**: Correlates customer ratings with sales performance to identify high-risk products

### Product Categories

The system manages four main product categories:

- **Whole Chicken**: Premium free-range whole birds, roasted and ready-to-serve
- **Chicken Parts**: Breasts, thighs, wings, drumsticks - fresh and prepared
- **Chicken Byproducts**: Liver pâté, stock, rendered fat, sausage - value-added products
- **Chicken Pastries**: Pot pies, empanadas, croissants - prepared convenience items

Each product has specific shelf life requirements, storage needs, and recipe dependencies that the system tracks and optimizes.

### Key Metrics Tracked

- **Sales Performance**: Revenue, quantity, average price per unit by product and time period
- **Waste Analytics**: Waste quantity, cost, and reasons (expired, damaged, overstock)
- **Inventory Risk**: Products approaching expiration dates
- **Forecast Accuracy**: Comparison of predicted vs. actual sales
- **Customer Sentiment**: Ratings and feedback correlated with sales performance
- **Recipe Costs**: Ingredient usage and costs across products
- **Regulatory Status**: FDA enforcement actions and recalls

### Business Impact

By using Save the Chickens, retailers can:
- **Reduce Waste**: Identify and address waste patterns before they become costly
- **Optimize Inventory**: Use AI forecasts to maintain optimal stock levels
- **Improve Profitability**: Balance pricing, discounts, and inventory to maximize revenue
- **Enhance Customer Satisfaction**: Track feedback and adjust products accordingly
- **Ensure Compliance**: Stay ahead of regulatory issues that could impact operations

The system transforms raw data into actionable insights, helping retailers make informed decisions that save money, reduce waste, and improve operations.

## Features

- **Natural Language Querying**: Ask questions in plain English about your chicken product data
- **Automated SQL Generation**: The agent automatically generates optimized BigQuery SQL queries
- **Waste Optimization**: Track and analyze waste patterns to reduce costs and improve efficiency
- **Stock Management**: Monitor inventory levels, due dates, and product expiration
- **Recipe Analysis**: Track ingredient usage and recipe costs across products
- **Comprehensive Analysis**: Built-in protocols for sales analysis, forecasting accuracy, customer sentiment, waste tracking, and regulatory compliance
- **Evaluation Framework**: Includes evaluation tools to measure agent performance on factual accuracy and completeness
- **Session Management**: Uses in-memory session service for conversation context

## Project Structure

```
save-the-chickens/
├── chickens_app/
│   ├── __init__.py
│   ├── agent.py              # Agent configuration and initialization
│   └── agent_instructions.txt # Detailed analysis protocols and guidelines
├── bigquery_source_data/      # Optional: CSV data files and setup script
│   ├── CustomerFeedback.csv
│   ├── ProductMasterData.csv
│   ├── product_sales.csv
│   ├── Recipes.csv
│   ├── WasteTracking.csv
│   └── setup_bigquery.sh      # Script to create dataset and load data
├── run_agent.py              # Main agent runner with async conversation handling
├── utils.py                  # Utility functions for agent invocation and evaluation
├── evaluate_agent.py         # Evaluation framework with custom metrics
├── evaluation_dataset.json   # Test dataset for agent evaluation
├── start_web.sh              # Helper script to start web UI with default app
├── requirements.txt          # Python dependencies
└── .env                       # Environment variables (create from template)
```

## Prerequisites

- Python 3.8 or higher
- Google Cloud Project with BigQuery enabled
- Service account credentials with BigQuery access
- Access to Vertex AI (for evaluation features)
- `bq` command-line tool (part of Google Cloud SDK) - for optional data setup

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd save-the-chickens
```

2. **Authenticate with Google Cloud Platform** (do this BEFORE creating the virtual environment):
```bash
# Install gcloud CLI if not already installed
# https://cloud.google.com/sdk/docs/install

# Authenticate using application default credentials
# IMPORTANT: Run this BEFORE activating any virtual environment
gcloud auth application-default login

# Set your default project (optional, can also be set in .env)
gcloud config set project <your_project>

# Verify authentication
gcloud auth list
```

**Important:** Always run `gcloud` commands outside of your virtual environment to avoid conflicts with gcloud's bundled Python dependencies. If you're already in a virtual environment, deactivate it first: `deactivate`

3. **Set up configuration:**
   - Create a `.env` file in the project root with the following variables:
     ```bash
     GOOGLE_GENAI_USE_VERTEXAI=1 
     GOOGLE_CLOUD_PROJECT=<your_project>
     GOOGLE_CLOUD_LOCATION=us-central1
     BIGQUERY_DATASET=save_the_chickens
     ```
     
     **Note:** `BIGQUERY_DATASET` is optional and defaults to `save_the_chickens` if not specified. `GOOGLE_CLOUD_PROJECT` is required.

4. **Set up BigQuery dataset and tables (Optional):**
   
   If you need to create the dataset and load sample data, use the provided setup script:
   
   ```bash
   # Make sure you're authenticated (step 2) and have bq CLI tool installed
   # IMPORTANT: Run this BEFORE creating virtual environment (bq/gcloud conflicts with venv)
   cd bigquery_source_data
   chmod +x setup_bigquery.sh
   ./setup_bigquery.sh
   ```
   
   This script will:
   - Create the dataset in the US region (if it doesn't exist)
   - Load CSV files as tables: `ProductMasterData`, `product_sales`, `CustomerFeedback`, `Recipes`, `WasteTracking`
   - Create a view `fda_chicken_enforcements` from the public FDA food enforcement dataset (filtered for chicken products)
   - Create a view `actuals_vs_forecast` that combines historical sales data with TimesFM AI-generated 30-day forecasts
   
   **Note:** The script reads `GOOGLE_CLOUD_PROJECT` and `BIGQUERY_DATASET` from your `.env` file.
   
   **Important:** Always run `bq` and `gcloud` commands outside of your virtual environment to avoid Python dependency conflicts.
   
   The `actuals_vs_forecast` view uses BigQuery's [`AI.FORECAST`](https://docs.cloud.google.com/bigquery/docs/timesfm-model) function with the TimesFM model to generate 30-day sales forecasts grouped by ProductNumber. It unions actual sales data with forecast predictions, making it easy to compare actuals vs forecasts in a single query. The TimesFM model is a foundation model pre-trained on billions of time-points, providing accurate forecasts without requiring model training.

5. Create a virtual environment (recommended):
```bash
python -m venv .adkvenv
source .adkvenv/bin/activate  # On Windows: .adkvenv\Scripts\activate
```

6. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Agent Configuration

The agent is configured dynamically from environment variables:
- **Project ID**: Set via `GOOGLE_CLOUD_PROJECT` in `.env` (required)
- **Dataset**: Set via `BIGQUERY_DATASET` in `.env` (optional, defaults to `save_the_chickens`)
- **Model**: `gemini-2.5-flash` (configured in `chickens_app/agent.py`)
- **Location**: `us-central1` (required for Vertex AI, set in `.env`)

The `.env` file is required when using Vertex AI. The `GOOGLE_GENAI_USE_VERTEXAI=1` setting ensures the agent uses Vertex AI endpoints instead of the default API.

**Important:** The project ID and dataset name are automatically injected into agent instructions at runtime from environment variables. No hardcoded values remain in the codebase.

To modify the model, edit `chickens_app/agent.py`:

```python
# Change model in agent.py
root_agent = Agent(
    model="gemini-2.5-flash",  # Change this to use a different model
    ...
)
```

**Note:** Project ID and dataset are configured via environment variables (`.env` file), not in the code. The agent instructions automatically use these values at runtime.

## Usage

### Running the Agent

#### Web Interface (Recommended)

Run the agent using the ADK web interface from the project root directory:

**Option 1: Use the helper script (recommended - opens browser automatically):**
```bash
chmod +x start_web.sh
./start_web.sh
# Or specify a custom port:
./start_web.sh 8080
```

The helper script automatically opens your browser to `http://localhost:8000/dev-ui/?app=chickens_app` with the app pre-selected.

**Option 2: Use adk web directly:**
```bash
adk web --port 8000
```

Then manually open your browser to:
- **Direct link with app selected**: [http://localhost:8000/dev-ui/?app=chickens_app](http://localhost:8000/dev-ui/?app=chickens_app)
- **Or manually select**: [http://localhost:8000](http://localhost:8000) and choose `chickens_app` from the dropdown

**Note:** 
- Run commands from the **root directory** that contains the `chickens_app/` folder
- The helper script (`start_web.sh`) automatically opens the browser with the `?app=chickens_app` parameter, so you don't need to manually select the app
- You can bookmark `http://localhost:8000/dev-ui/?app=chickens_app` for quick access
- For more details on running ADK agents, see the [ADK documentation](https://google.github.io/adk-docs/get-started/python/#run-your-agent)

#### Command-Line Interface

Alternatively, run the agent using the ADK CLI:

```bash
adk run chickens_app
```

#### Programmatic Usage

The agent can also be invoked programmatically using the `run_agent` module:

```python
import asyncio
from run_agent import run_conversation

async def main():
    response = await run_conversation("What tables are available in the dataset?")
    print(response["response"])
    print("Tool calls:", response["predicted_trajectory"])

asyncio.run(main())
```

Or use the utility function for synchronous access:

```python
from utils import get_agent_response

response = get_agent_response("How many chicken products are in the master data?")
print(response["response"])
```

### Evaluation

Run the evaluation framework to assess agent performance:

```bash
python evaluate_agent.py
```

This will:
- Load test cases from `evaluation_dataset.json`
- Execute each prompt through the agent
- Evaluate responses using custom metrics (factual accuracy, completeness, tool usage)
- Generate evaluation results in `eval_results/` directory
- Display summary metrics including average completeness and factual accuracy scores

Evaluation metrics:
- **Factual Accuracy**: Measures correctness of factual information (ratings 1-5)
- **Completeness**: Assesses whether all requested information is provided (ratings 1-5)
- **Tool Usage**: Tracks proper use of BigQuery tools (e.g., `list_table_ids`)

## Agent Capabilities

The agent follows a comprehensive analysis protocol defined in `agent_instructions.txt`. Key capabilities include:

### Sales Analysis
- Calculate KPIs: Total Revenue, Total Quantity, Average Price Per Unit
- Identify top/bottom products by revenue and quantity
- Year-over-year seasonality analysis
- Track products approaching due dates to prevent waste

### Customer Analysis
- Correlate product ratings with sales performance
- Identify high-risk products (high revenue, poor reviews)
- Analyze customer feedback themes
- Product substitution analysis by category

### Waste Optimization
- Track waste patterns by product, reason, and cost
- Identify products at risk of expiration
- Calculate total waste costs and trends
- Recommend discount strategies for products near expiration
- Optimize delivery schedules to reduce overstock

### Recipe and Ingredient Analysis
- Analyze recipe costs per product
- Track ingredient usage across multiple products
- Suggest recipe modifications to reduce waste
- Procurement planning based on ingredient usage

### Forecasting Analysis
- Calculate forecast accuracy (absolute and percentage error) using the `actuals_vs_forecast` view
- Assess confidence interval reliability by checking if actuals fall within prediction intervals
- Detect volatility patterns and consecutive days with large variance (±20% or more)
- Compare actual sales vs forecasted values across different products and time periods
- Integrate waste data into forecast accuracy analysis

### Regulatory Compliance
- Cross-reference FDA enforcement actions with sales data
- Provide root cause analysis for sales anomalies

### Data Integrity
- Validate data quality (negative values, missing links, rating ranges)
- Report data issues automatically

## Dataset Schema

The agent works with the following tables and views in the dataset:

### Tables

- `ProductMasterData`: Product master data with ProductNumber, ProductDescription, ProductCategory, ShelfLifeDays, StorageRequirements, and DueDate
- `product_sales`: Sales transaction data with SaleID, SaleDate, DeliveryDate, ProductNumber, SalesQuantity, PricePerUnit, TotalRevenue, and DueDate
- `CustomerFeedback`: Customer feedback and ratings with CustomerName, ProductName, FeedbackDate, Rating, and Description
- `Recipes`: Recipe data with RecipeID, ProductID, IngredientName, IngredientQuantity, Unit, and PreparationMethod
- `WasteTracking`: Waste tracking data with WasteID, ProductID, WasteDate, WasteQuantity, WasteReason, Cost, and Notes

### Views

- `actuals_vs_forecast`: Combined view of historical sales (actuals) and AI-generated 30-day forecasts
  - Contains: `event_timestamp`, `ProductNumber`, `quantity_value`, `confidence_level`, `prediction_interval_lower_bound`, `prediction_interval_upper_bound`, `ai_forecast_status`, `data_type` ('Actual' or 'Forecast')
  - Uses BigQuery's [`AI.FORECAST`](https://docs.cloud.google.com/bigquery/docs/timesfm-model) function with the TimesFM model to generate forecasts grouped by ProductNumber
  - TimesFM is a foundation model pre-trained on billions of time-points, providing accurate forecasts without model training
  - Allows easy comparison of actual sales performance vs predicted values
  
- `fda_chicken_enforcements`: FDA regulatory actions filtered for chicken products (view from `bigquery-public-data.fda_food.food_enforcement`)

## Output Format

The agent returns structured responses with:
- Natural language answers to questions
- Markdown tables for summarized data
- Interpretations and insights, not just raw data
- Suggestions for follow-up questions


## Development

### Adding New Evaluation Cases

Edit `evaluation_dataset.json` to add new test cases:

```json
{
    "prompt": "Your test question here",
    "reference": "Expected answer or ground truth"
}
```

### Modifying Agent Instructions

Update `chickens_app/agent_instructions.txt` to change agent behavior, add new analysis protocols, or modify SQL optimization guidelines.

### Custom Metrics

Add custom evaluation metrics in `evaluate_agent.py` by creating new `PointwiseMetric` or trajectory metrics.

## Troubleshooting

**Authentication Errors**
- Run `gcloud auth application-default login` to set up Application Default Credentials (see Configuration section)
- Verify authentication: `gcloud auth list`
- Verify `.env` file exists in project root with required variables
- Check that `GOOGLE_GENAI_USE_VERTEXAI=1` is set in `.env`
- Verify `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` match your Vertex AI setup
- Ensure your authenticated account has BigQuery Data Viewer and Job User roles
- If using service account: set `GOOGLE_APPLICATION_CREDENTIALS` environment variable pointing to your service account JSON key

**Import Errors**
- Make sure virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check that you're using Python 3.8+

**Agent Not Finding Instructions**
- Ensure `agent_instructions.txt` exists in `chickens_app/` directory
- Check file permissions and path resolution

**Evaluation Failures**
- Verify `evaluation_dataset.json` is valid JSON
- Check that prompts in evaluation dataset are appropriate for your dataset
- Ensure Vertex AI API is enabled in your Google Cloud project

## License

This project is licensed under the Apache License 2.0.

