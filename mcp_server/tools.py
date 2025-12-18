import os
import random
import uuid
import json
import httpx
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

from mcp import StdioServerParameters
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams

def get_local_mcp_toolset():
    """
    Configures and returns the Local MCP toolset (Marketing Agent Client, Store Temp).
    
    This connects to the `mcp_server.server` process via Stdio.
    """
    logger.info("Configuring Local MCP Toolset (Stdio)...")
    
    # We run the server module as a subprocess
    server_params = StdioServerParameters(
        command="python", # Or usage of sys.executable
        args=["-m", "mcp_server.server"],
        env=os.environ.copy() # Pass env vars for configuration
    )
    
    # Wrap in StdioConnectionParams to allow setting a timeout (default is 5s, we need more for LLM)
    connection_params = StdioConnectionParams(
        server_params=server_params,
        timeout=300.0 # 5 minutes timeout for A2A LLM calls
    )
    
    tools = MCPToolset(
        connection_params=connection_params
    )
    logger.info("Local MCP Toolset configured.")
    return tools
