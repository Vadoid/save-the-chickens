import os
from typing import Any, Dict, List
from mcp.server.fastmcp import FastMCP
from google.cloud import bigquery
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bigquery_mcp_server")

# Initialize FastMCP
mcp = FastMCP("bigquery-server")

# Get configuration from environment
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
DATASET_ID = os.getenv("BIGQUERY_DATASET", "save_the_chickens")

if not PROJECT_ID:
    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")

logger.info(f"Starting BigQuery MCP Server for project {PROJECT_ID}, dataset {DATASET_ID}")

# Initialize BigQuery Client
client = bigquery.Client(project=PROJECT_ID)

@mcp.tool()
def query_dataset(query: str) -> str:
    """
    Execute a SQL query against the BigQuery dataset.
    
    Args:
        query: The SQL query to execute.
    
    Returns:
        A string representation of the query results (markdown table).
    """
    try:
        # Basic safety check (very primitive, but better than nothing)
        if "DROP" in query.upper() or "DELETE" in query.upper() or "UPDATE" in query.upper():
             return "Error: Only SELECT queries are allowed."

        logger.info(f"Executing query: {query}")
        query_job = client.query(query)
        results = query_job.result()
        
        # Convert to dataframe for easy string representation
        df = results.to_dataframe()
        
        if df.empty:
            return "Query returned no results."
            
        return df.to_markdown(index=False)
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        return f"Error executing query: {str(e)}"

@mcp.tool()
def list_tables() -> str:
    """
    List all tables in the configured dataset.
    
    Returns:
        A list of table names.
    """
    try:
        dataset_ref = client.dataset(DATASET_ID)
        tables = client.list_tables(dataset_ref)
        table_names = [table.table_id for table in tables]
        return "\n".join(table_names)
    except Exception as e:
        return f"Error listing tables: {str(e)}"

@mcp.tool()
def get_table_schema(table_name: str) -> str:
    """
    Get the schema of a specific table.
    
    Args:
        table_name: The name of the table.
        
    Returns:
        A string description of the schema.
    """
    try:
        dataset_ref = client.dataset(DATASET_ID)
        table_ref = dataset_ref.table(table_name)
        table = client.get_table(table_ref)
        
        schema_info = []
        for schema_field in table.schema:
            schema_info.append(f"{schema_field.name}: {schema_field.field_type} ({schema_field.mode})")
            
        return "\n".join(schema_info)
    except Exception as e:
        return f"Error getting schema for table {table_name}: {str(e)}"

@mcp.tool()
def get_store_temperature(store_id: str) -> str:
    """
    Get the current temperature of the store's freezer/fridge units.
    
    Args:
        store_id: The ID of the store (e.g., 'S001').
        
    Returns:
        A JSON string containing temperature data for units.
    """
    import random
    import json
    
    # Mock logic: Generate random temperatures
    # Most are good (-20C to -18C), some are warning (-15C), rare critical (-5C)
    
    units = ["Freezer-1", "Freezer-2", "Fridge-Main", "Display-Case"]
    data = {"store_id": store_id, "units": []}
    
    for unit in units:
        # 90% chance of good temp, 10% chance of issue
        if random.random() > 0.1:
            temp = round(random.uniform(-22.0, -18.0), 1)
            status = "OK"
        else:
            temp = round(random.uniform(-15.0, -5.0), 1)
            status = "WARNING" if temp < -10 else "CRITICAL"
            
        data["units"].append({
            "unit_id": unit,
            "temperature_celsius": temp,
            "status": status
        })
        
    return json.dumps(data, indent=2)

if __name__ == "__main__":
    mcp.run()
