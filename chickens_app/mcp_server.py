import os
import random
import google.auth
import google.auth.transport.requests
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams 
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

MAPS_API_KEY = os.getenv('MAPS_API_KEY', 'no_api_found')
MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp" 
BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp" 

def get_maps_mcp_toolset():
    """
    Configures and returns the Maps MCP toolset.
    
    This toolset provides access to Google Maps Platform capabilities via MCP,
    including place search, directions, and distance calculations.
    
    Returns:
        MCPToolset: A configured toolset instance for Maps.
    """
    logger.info("Configuring Maps MCP Toolset...")
    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=MAPS_MCP_URL,
            headers={    
                "X-Goog-Api-Key": MAPS_API_KEY
            }
        )
    )
    logger.info("Maps MCP Toolset configured.")
    return tools


def get_bigquery_mcp_toolset():   
    """
    Configures and returns the BigQuery MCP toolset with Application Default Credentials (ADC).
    
    This toolset provides access to BigQuery datasets, tables, and query execution
    capabilities via MCP. It automatically handles OAuth2 authentication using
    the environment's default credentials.
    
    Returns:
        MCPToolset: A configured toolset instance for BigQuery.
    """
    logger.info("Configuring BigQuery MCP Toolset...")
    
    # 1. Get default credentials (ADC)
    # This automatically finds credentials from `gcloud auth application-default login`
    # or the service account attached to the compute instance.
    credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/bigquery"]
    )

    # 2. Refresh credentials to get a valid access token
    # We need the raw token to pass it in the Authorization header.
    credentials.refresh(google.auth.transport.requests.Request())
    oauth_token = credentials.token
        
    # 3. Construct Headers
    # - Authorization: Bearer token for authentication
    # - x-goog-user-project: Required for billing/quota attribution
    HEADERS_WITH_OAUTH = {
        "Authorization": f"Bearer {oauth_token}",
        "x-goog-user-project": project_id
    }

    # 4. Initialize Toolset
    # We use StreamableHTTPConnectionParams to connect to the remote MCP server.
    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=BIGQUERY_MCP_URL,
            headers=HEADERS_WITH_OAUTH
        )
    )
    logger.info("BigQuery MCP Toolset configured.")
    return tools

def get_store_temperature(store_id: str) -> str:
    """
    Get the current temperature of the store's freezer/fridge units.
    
    This function simulates retrieving real-time IoT sensor data from store units.
    It returns temperature readings and status (OK, WARNING, CRITICAL) for
    various units like Freezers, Fridges, and Display Cases.
    
    Args:
        store_id: The ID of the store (e.g., 'S001').
        
    Returns:
        str: A JSON string containing temperature data for units.
             Example:
             {
               "store_id": "S001",
               "units": [
                 {"unit_id": "Freezer-1", "temperature_celsius": -19.5, "status": "OK"},
                 ...
               ]
             }
    """
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
