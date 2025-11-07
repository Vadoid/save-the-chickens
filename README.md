# Save the Chickens - BigQuery ADK Agent

AI agent for chicken product retail operations using Google's ADK. Provides natural language querying, waste optimization, inventory management, and sales forecasting.

## Quick Start

**What it does:**
- Natural language queries on BigQuery data (sales, inventory, waste, recipes, customer feedback)
- AI-powered 30-day sales forecasting using TimesFM
- Waste tracking and expiration risk alerts
- Recipe cost analysis and ingredient tracking
- FDA compliance monitoring

**Setup:**
```bash
# 1. Authenticate (run BEFORE creating venv)
gcloud auth application-default login
gcloud config set project <your_project>

# 2. Create .env file
cat > .env << EOF
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=<your_project>
GOOGLE_CLOUD_LOCATION=us-central1
BIGQUERY_DATASET=save_the_chickens
EOF

# 3. Setup BigQuery (optional - for sample data)
cd bigquery_source_data && ./setup_bigquery.sh && cd ..

# 4. Install and run
python -m venv .adkvenv
source .adkvenv/bin/activate
pip install -r requirements.txt
./start_web.sh
```

## Configuration

**Required `.env` variables:**
```bash
GOOGLE_GENAI_USE_VERTEXAI=1          # Use Vertex AI
GOOGLE_CLOUD_PROJECT=<project_id>    # Your GCP project
GOOGLE_CLOUD_LOCATION=us-central1    # Vertex AI location
BIGQUERY_DATASET=save_the_chickens   # Optional, defaults to save_the_chickens
ADK_LOG_LEVEL=WARNING                # Optional, reduces verbosity
```

**Agent settings:**
- Model: `gemini-2.5-flash` (edit in `chickens_app/agent.py`)
- Project/Dataset: Auto-injected from `.env` at runtime

## Usage

**Web UI (recommended):**
```bash
./start_web.sh  # Opens http://localhost:8000/dev-ui/?app=chickens_app
```

**CLI:**
```bash
adk run chickens_app
```

**Programmatic:**
```python
from utils import get_agent_response
response = get_agent_response("What products are at risk of expiration?")
print(response["response"])
```

## Use Cases

**Sales & Inventory:**
- "What are the top 5 products by revenue this month?"
- "Which products are approaching expiration?"
- "Show me sales trends for chicken breasts"

**Waste Optimization:**
- "What's our total waste cost this quarter?"
- "Which products have the highest waste rates?"
- "Recommend discount strategies for products expiring soon"

**Customer Analysis:**
- "What products have the worst customer ratings?"
- "Show me feedback for whole roasted chicken"
- "Which high-revenue products have poor reviews?"

**Recipe & Ingredients:**
- "What ingredients are in product 1001?"
- "Which ingredients are used across multiple products?"
- "What's the shelf life of ingredients in chicken pot pie?"

**Forecasting:**
- "Compare actual vs forecasted sales for last month"
- "What's the forecast accuracy for product 1002?"
- "Show me products with volatile forecast errors"

**Compliance:**
- "Are there any FDA recalls for chicken products?"
- "Check for regulatory actions affecting our sales"

## Dataset Schema

**Tables:**
- `ProductMasterData`: Products (ProductNumber, Description, Category, ShelfLifeDays, RecipeID)
- `product_sales`: Sales transactions (SaleID, SaleDate, ProductNumber, Quantity, Revenue)
- `CustomerFeedback`: Reviews (CustomerName, ProductName, Rating, Description)
- `Recipes`: Ingredients (RecipeID, IngredientName, Quantity, IngredientShelfLifeDays)
- `WasteTracking`: Waste records (ProductID, WasteDate, Quantity, Reason, Cost)

**Views:**
- `actuals_vs_forecast`: Historical sales + AI-generated 30-day forecasts
- `products_with_recipes`: Products joined with ingredients
- `customer_feedback_with_products`: Reviews joined with products (fuzzy matched)
- `fda_chicken_enforcements`: FDA actions for chicken products

## Evaluation

```bash
python evaluate_agent.py
```

Tests agent on `evaluation_dataset.json`, measures factual accuracy and completeness.

## Project Structure

```
save-the-chickens/
├── chickens_app/
│   ├── agent.py              # Agent config
│   └── agent_instructions.txt # Analysis protocols
├── bigquery_source_data/     # CSV files + setup script
├── run_agent.py             # Agent runner
├── evaluate_agent.py        # Evaluation framework
└── start_web.sh             # Web UI launcher
```

## Troubleshooting

**Authentication:**
- Run `gcloud auth application-default login` (outside venv)
- Verify `.env` has correct `GOOGLE_CLOUD_PROJECT`
- Ensure account has BigQuery Data Viewer and Job User roles

**Import errors:**
- Activate venv: `source .adkvenv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

**Agent issues:**
- Check `agent_instructions.txt` exists in `chickens_app/`
- Verify Vertex AI API is enabled in GCP project
- Check logs for specific error messages

## License

Apache License 2.0
